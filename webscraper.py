#!/usr/bin/python

import sys
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

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
    url = str_url

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
