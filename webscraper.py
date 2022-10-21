#!/usr/bin/env python3

import sys
import argparse
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
from validate_email_address import validate_email

def web_scraper(str_url, arg_e, arg_t, arg_id, arg_a, arg_w, arg_m):
    # Selenium Driver Set-up #
    service = Service(executable_path=GeckoDriverManager().install())
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options, service=service)

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
    emails = set()
    values = set()
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
#        try:
#            response = requests.get(url)
#        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
#            print('Excpetion caught')
#            continue

#        new_emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', response.text, re.I))
#        emails.update(new_emails)

        ## IF DYNAMIC PAGE ##
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        if arg_e:
            new_emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', driver.page_source, re.I))
            emails.update(new_emails)

        if arg_w:
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, arg_a)))
            except:
                pass
            finally:
                pass

        if arg_t:
            try:
                elements = driver.find_elements(By.TAG_NAME, arg_t)
                for element in elements:
                    values.add(element.text)
            except:
                pass

        if arg_id:
            try:
                elements = driver.find_elements(By.ID, arg_id)
                for elements in elements:
                    values.add(element.text)
            except:
                pass

        if arg_a:
            try:
#                elements = driver.find_elements(By.CLASS_NAME, arg_a)
                elements = soup.find_all('span', {'class': 'client'})
                for element in elements:
#                    values.add(element.text)
                    values.add(element.get_text())
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
                if link.startswith(original_url):
                    if not link in unscraped and not link in scraped:
                        unscraped.append(link)

    driver.quit()

    if arg_e:
        email_validator(emails)

    df = pd.DataFrame(values, columns=['Requested values'])
    df.to_csv('values.csv', index=False)

def email_validator(email_list):
    for e in email_list.copy():
        if not validate_email(e, verify=True):
            print(f'Email {e} is not valid. Removing from list')
            email_list.remove(e)

    df = pd.DataFrame(email_list, columns=['Email'])
    df.to_csv('email.csv', index=False)

def main():
    ## implement argparser ##
    parser = argparse.ArgumentParser(usage='./webscraper.py [-h] DOMAIN [-e] [-t TAG] [-id ID] [-a ATTR] [-w WAIT] [-m MAX]')
    parser.add_argument('domain', help='specify the domain to be scraped', metavar='DOMAIN')
    parser.add_argument('-e', '--email', help='scrape for emails, default is False', action='store_true')
    tag_grp = parser.add_argument_group('tag option')
    tag_grp.add_argument('-t', '--tag', type=str, help='specify a tag to scrape')
    tag_grp.add_argument('-id', type=str, help='specify a tag ID to scrape')
    tag_grp.add_argument('-a', '--attr', type=str, help='specify a class name to scrape')
    parser.add_argument('-w', '--wait', help='time to allow scripts to load before scraping, default is 0')
    parser.add_argument('-m', '--max', type=int, help='maximum number of URLs to scrape, default is 50')
    args = parser.parse_args()
    print(args)

    web_scraper(args.domain, args.email, args.tag, args.id, args.attr, args.wait, args.max)

### BOILERPLATE ###
if __name__ == "__main__":
    main()
