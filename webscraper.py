#!/usr/bin/env python3

import sys
import argparse
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedTagNameException
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
import csv
from itertools import zip_longest
from validate_email_address import validate_email

def web_scraper(str_url, arg_e, arg_t, arg_id, arg_a, arg_w, arg_m):
    # Selenium Driver Set-up #
    service = Service(executable_path=GeckoDriverManager().install())
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options, service=service)

    # Create lists for Expected Conditions #
    exp_cond_t = []
    exp_cond_id = []
    exp_cond_a = []

    original_url = str_url
    # validate url schema #
    if not urlsplit(original_url)[0]:
        original_url = 'http://' + original_url

    try:
        driver.get(original_url)
    except:
        driver.quit()
        print(f'Error navigating to {original_url}. Please ensure the URL was entered correctly.')
        return

    unscraped = deque([driver.current_url])
    scraped = set()

    # create dictionary with values containing sets #
    data = {}
    if arg_e:
        data['email'] = set()
    if arg_t:
        for t in arg_t:
            data[t] = set()
    if arg_id:
        for i in arg_id:
            data[i] = set()
    if arg_a:
        for a in arg_a:
            data[a] = set()

    wait_time = arg_w
    scrape_max = arg_m

    if not arg_m:
        scrape_max = 50
    if not arg_w:
        wait_time = 0

    while len(unscraped) and len(scraped) < scrape_max:
        # re-initalize elements #
        elements = ()
        url = unscraped.popleft()
        scraped.add(url)

        parts = urlsplit(url)

        base_url = f'{parts[0]}://{parts[1]}'
        if '/' in parts[2]:
            path = url[:url.rfind('/') + 1]
        else:
            path = url

        print(f'Crawling URL {url}')

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        if arg_w:
            try:
                if arg_t:
                    for t in arg_t:
                        exp_cond_t.append(EC.presence_of_element_located((By.TAG_NAME, t)))
                if arg_id:
                    for i in arg_id:
                        exp_cond_id.append(EC.presence_of_element_located((By.ID, i)))
                if arg_a:
                    for a in arg_a:
                        exp_cond_a.append(EC.presence_of_element_located((By.CLASS_NAME, a)))
                wait = WebDriverWait(driver, wait_time)
                wait.until(EC.any_of(
                    *exp_cond_t,
                    *exp_cond_id,
                    *exp_cond_a))
                if arg_a and arg_t and arg_id:
                    wait.until(EC.any_of(*exp_cond_t, *exp_cond_id, *exp_cond_a))
                elif arg_a and arg_t:
                    wait.until(EC.any_of(*exp_cond_t, *exp_cond_a))
                elif arg_a and arg_id:
                    wait.until(EC.any_of(*exp_cond_id, *exp_cond_a))
                elif arg_t and arg_id:
                    wait.until(EC.any_of(*exp_cond_t, *exp_cond_id))
                elif arg_a:
                    wait.until(EC.any_of(*exp_cond_a))
                elif arg_t:
                    wait.until(EC.any_of(*exp_cond_t))
                else:
                    wait.until(EC.any_of(*exp_cond_id))
            except NoSuchElementException:
                print('no such element exception caught')
                pass
            except UnexpectedTagNameException:
                print('unexpected tag name exception caught')
                pass
            except TimeoutException:
                print('timeout exception caught')
                pass
            finally:
                pass
        
        if arg_e:
            new_emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', driver.page_source, re.I))
            data['email'].update(new_emails)

        if arg_t:
            try:
                for t in arg_t:
                    elements = driver.find_elements(By.TAG_NAME, t)
                    for element in elements:
                        data[t].add(element.text)
            except:
                pass

        if arg_id:
            try:
                for i in arg_id:
                    elements = driver.find_elements(By.ID, i)
                    for element in elements:
                        data[i].add(element.text)
            except:
                pass

        if arg_a:
            try:
                for a in arg_a:
                    elements = driver.find_elements(By.CLASS_NAME, a)
                    for element in elements:
                        data[a].add(element.text)
            except:
                pass

        for anchor in soup.find_all('a'):
            if 'href' in anchor.attrs:
                link = anchor.attrs['href']
            else:
                link = ''

            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link

            if not link.endswith('.gz'):
                if link.startswith(base_url):
                    if not link in unscraped and not link in scraped:
                        unscraped.append(link)

    driver.quit()

    if arg_e:
        email_validator(data['email'])

    ## write to csv ##
    # define columns #
    col_names=[]
    for k in data.keys():
        col_names.append(k.title())

    # write to file #
    with open('scraped-data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(col_names)

        for vals in zip_longest(*data.values()):
            row = vals
            writer.writerow(row)


def email_validator(email_list):
    for e in email_list.copy():
        if not validate_email(e, verify=True):
            print(f'Email {e} is not valid. Removing from list')
            email_list.remove(e)

    return email_list


def main():
    ## implement argparser ##
    parser = argparse.ArgumentParser(usage='./webscraper.py [-h] DOMAIN [-e] [-t TAG] [-id ID] [-a ATTR] [-w WAIT] [-m MAX]')
    parser.add_argument('domain', help='specify the domain to be scraped', metavar='DOMAIN')
    parser.add_argument('-e', '--noemail', help='scrape for emails, default is True', action='store_false')
    tag_grp = parser.add_argument_group('tag option')
    tag_grp.add_argument('-t', '--tag', type=str, action='append', help='specify a tag to scrape')
    tag_grp.add_argument('-id', type=str, action='append', help='specify a tag ID to scrape')
    tag_grp.add_argument('-a', '--attr', type=str, action='append', help='specify a class name to scrape')
    parser.add_argument('-w', '--wait', type=int, help='time to allow scripts to load before scraping, default is 0')
    parser.add_argument('-m', '--max', type=int, help='maximum number of URLs to scrape, default is 50')
    args = parser.parse_args()
    print(args)

    web_scraper(args.domain, args.noemail, args.tag, args.id, args.attr, args.wait, args.max)

### BOILERPLATE ###
if __name__ == "__main__":
    main()
