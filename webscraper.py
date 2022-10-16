#!/usr/bin/env python3

import sys
import argparse
import re
import requests
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd
from validate_email_address import validate_email

def web_scraper(str_url, arg_t, arg_a, arg_m):
    original_url = str_url
    tag = arg_t
    attr = arg_a
    scrape_max = arg_m

    unscraped = deque([original_url])
    scraped = set()
    emails = set()
    values = set()

    scrape_max = 50

    while len(unscraped) and len(scraped) < scrape_max:
        url = unscraped.popleft()
        scraped.add(url)

        parts = urlsplit(url)

        base_url = f'{parts[0]}://{parts[1]}'
        if '/' in parts[2]:
            path = url[:url.rfind('/') + 1]
        else:
            path = url

        print(f'Crawling URL {url}')
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print('Excpetion caught')
            continue

        new_emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

        if tag:
            for t in soup.find_all(tag):
                if attr in t.attrs:
                    values.append(t.attrs[attr])

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
    parser = argparse.ArgumentParser(usage='./webscraper.py [-h] DOMAIN [-t TAG -a ATTR] [-m MAX]')
    parser.add_argument('domain', help='specify the domain to be scraped', metavar='DOMAIN')
    tag_grp = parser.add_argument_group('tag option')
    tag_grp.add_argument('-t', '--tag', type=str, help='specify a tag to scrape')
    tag_grp.add_argument('-a', '--attr', type=str, help='specify a tag attribute to scrape')
    parser.add_argument('-m', '--max', type=int, help='maximum number of URLs to scrape')
    args = parser.parse_args()
    print(args)

    web_scraper(args.domain, args.tag, args.attr, args.max)

### BOILERPLATE ###
if __name__ == "__main__":
    main()
