#!/usr/bin/python

import sys
import re
import requests
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

def check_static(str_url):
    req = Request(
            url=str_url,
            headers={'User-Agent': 'Mozilla/5.0'}
            )

    webpage = urlopen(req).read()
    text = webpage.decode()

    if re.findall('(.*?)', text):
        return 1
    else:
        return 0

def web_scraper(str_url):
    original_url = str_url

    unscraped = deque([original_url])
    scraped = set()
    emails = set()

    num_to_scrape = 50

    while len(unscraped) and len(scraped) < num_to_scrape:
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

        new_emails = set(re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.co', response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

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

    df = pd.DataFrame(emails, columns = ['Email'])
    df.to_csv('email.csv', index = False)

def main():
    ## implement argparser ##
    ## len(sys.argv) will suffice for now ##
    if len(sys.argv) == 2:
        domain = sys.argv[1]
    else:
        print(f'You must provide the domain to be scraped.\nUsage: ./webscraper [DOMAIN]')
        return

    if check_static(domain):
        web_scraper(domain)
    else:
        print(f'The domain {domain} is not a static page. Only static webpages are currently supported.')

### BOILERPLATE ###
if __name__ == "__main__":
    main()
