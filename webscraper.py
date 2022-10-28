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
from collections import deque
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest
from validate_email_address import validate_email

###
# crawl through pages searching for elements
#
# @param {str} str_url - initial URL
# @param {bool} arg_e - switch for scraping emails
# @param {bool} arg_nv - switch for validating email list
# @param {list} arg_t - tag names to scrape
# @param {list} arg_id - class ID's to scrape
# @param {list} arg_c - class names to scrape
# @param {int} arg_w - maximum time to wait for page to load elements
# @param {int} arg_m - maximum number pages to scrape
# @param {str} arg_o - filename to write results to
###
def web_scraper(str_url, arg_e, arg_nv, arg_t, arg_id, arg_c, arg_w, arg_m, arg_o):
    # Selenium Driver Set-up #
    service = Service(executable_path=GeckoDriverManager().install())
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options, service=service)

    # Initialize list for Expected Conditions #
    ec_list = []

    original_url = str_url
    # Validate URL schema #
    if not urlsplit(original_url)[0]:
        original_url = 'http://' + original_url

    # Check if URL is accessible #
    try:
        driver.get(original_url)
    except:
        driver.quit()
        print(f'Error navigating to {original_url}. Please ensure the URL was entered correctly.')
        return

    # Initialize lists for URLs to scrape and visited URLs #
    unscraped = deque([driver.current_url])
    scraped = set()

    # Initialize dictionary for data #
    data = {}
    if arg_e:
        data['email'] = set()
    if arg_t:
        for t in arg_t:
            data[t] = set()
    if arg_id:
        for i in arg_id:
            data[i] = set()
    if arg_c:
        for c in arg_c:
            data[c] = set()

    wait_time = 0
    scrape_max = 0

    if arg_w:
        wait_time = arg_w
    if arg_m:
        scrape_max = arg_m

    while len(unscraped) and (scrape_max == 0 or len(scraped) < scrape_max):
        # Re-initalize elements #
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

        # Load URL in Selenium browser #
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Add wait conditions for WebDriverWait #
        if arg_w:
            try:
                if arg_t:
                    for t in arg_t:
                        ec_list.append(EC.presence_of_element_located((By.TAG_NAME, t)))
                if arg_id:
                    for i in arg_id:
                        ec_list.append(EC.presence_of_element_located((By.ID, i)))
                if arg_c:
                    for c in arg_c:
                        ec_list.append(EC.presence_of_element_located((By.CLASS_NAME, c)))
                wait = WebDriverWait(driver, wait_time)
                wait.until(EC.any_of(*ec_list))
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
        
        # Find all strings matching RegEx for email addresses #
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

        if arg_c:
            try:
                for c in arg_c:
                    elements = driver.find_elements(By.CLASS_NAME, c)
                    for element in elements:
                        data[c].add(element.text)
            except:
                pass

        # Find all links #
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
    
    # Close Selenium browser #
    driver.quit()

    if arg_e and arg_nv:
        email_validator(data['email'])

    ## write to csv ##
    # define columns #
    filename = 'scraped-data.csv'
    if arg_o:
        filename = arg_o
    col_names=[]
    for k in data.keys():
        col_names.append(k.title())

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(col_names)

        for vals in zip_longest(*data.values()):
            row = vals
            writer.writerow(row)


###
# check list of emails to see if SMTP server can be reached
#
# @param {list/set} email_list
###
def email_validator(email_list):
    for e in email_list.copy():
        if not validate_email(e, verify=True):
            print(f'Email {e} is not valid. Removing from list')
            email_list.remove(e)

    return email_list


def main():
    ## implement argparser ##
    parser = argparse.ArgumentParser(usage='./webscraper.py [-h] DOMAIN [-e] [-t TAG] [-id ID] [-c CLASSNAME] [-w WAIT] [-m MAX] [-o OUTFILE]')
    parser.add_argument('domain', help='specify the domain to be scraped', metavar='DOMAIN')
    parser.add_argument('-e', '--noemail', help='scrape for emails, default is True', action='store_false')
    parser.add_argument('-nv', '--novalidate', help='do not validate email list', action='store_false')
    tag_grp = parser.add_argument_group('tag option')
    tag_grp.add_argument('-t', '--tag', type=str, action='append', help='specify a tag to scrape')
    tag_grp.add_argument('-id', type=str, action='append', help='specify a tag ID to scrape')
    tag_grp.add_argument('-c', '--classname', type=str, action='append', help='specify a class name to scrape')
    parser.add_argument('-w', '--wait', type=int, help='time to allow scripts to load before scraping, default is 0')
    parser.add_argument('-m', '--max', type=int, help='maximum number of URLs to scrape')
    parser.add_argument('-o', '--outfile', type=str, help='specify a filename to write results to, default is "scraped-data.csv"')
    args = parser.parse_args()
    print(args)

    web_scraper(args.domain, args.noemail, args.novalidate, args.tag, args.id, args.classname, args.wait, args.max, args.outfile)

### BOILERPLATE ###
if __name__ == "__main__":
    main()
