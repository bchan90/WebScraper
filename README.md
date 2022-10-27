## WebScraper
An automated webscraper that crawls through the specified domain, looking for user-defined elements and email addresses.
The results of the scraping is written to a CSV file named 'scraped-data.csv' after completion of the script.

## Requirements and Installation
There are several modules that need to be installed prior to running the webscraper.
#### Selenium
```
pip install -U selenium
```
Make sure the ```-U``` flag is included as the latest version may not be installed and is necessary for WebScraper to run properly.

[PyPi Selenium](https://pypi.org/project/selenium/)
#### Webdriver Manager for Python
```
pip install webdriver-manager
```
[Webdriver Manager for Python Github](https://github.com/SergeyPirogov/webdriver_manager)
#### BeautifulSoup4
```
pip install beautifulsoup4
```
[PyPi BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
#### Pandas
```
pip install pandas
```
[Pandas Project](https://pandas.pydata.org/)
#### validate-email-address
```
pip install validate-email-address
```
[PyPi validate-email-address](https://pypi.org/project/validate-email-address/)

## How to Use
The script has one required positional argument, which is the starting domain to scrape.
Without specifying any additional options, this will scrape the domain(s) for any email addresses.
There are additional options that can be specified such as:
* -e or --noemail: switches the default behavior of the script so it does not scrape for email addresses.
* -t or --tag: allows for the user to specify a specific tag name to scrape for.
* -id: allows for the user to specify a specific class ID name to scrape for.
* -a or --attr: allows for the user to specify a specific class name to scrape for.
* -w or --wait: allows for the user to specify the maximum amount of time to wait (in seconds) to allow certain page elements to load (default is 0).
* -m or --max: allows for the user to specify the maximum number of domains to scrape (default is 50).

Note: the ```-t```, ```-id```, and ```-a``` arguments may be specified multiple times to look for more than one of those elements.
Examples of how to use these arguments can be found below.
### On Linux
To run the help command for Webscraper:
```
./webscraper.py -h
```
To execute the script in Linux in its most basic form:
```
./webscraper.py example.com
```
This will scrape example.com and any linked pages (up to 50) for email addresses.
```
./webscraper.py example.com -e -m 20
```
This will scrape example.com and any linked pages (up to 20). Because the '-e' option is specified, this will simply crawl the pages and not scrape for any information.
```
./webscraper.py example.com -t h3 -w 3
```
This will scrape example.com for the tag \<h3\>, as well as email addresses. The script will wait until the presence of the \<h3\> tag is found, or up to 3 seconds, whichever comes first.
```
./webscraper.py example.com -e -t h3 -a students -a teachers
```
This will scrape example.com for the tag \<h3\> and any elements with the class name 'students' and 'teachers'. This will not scrape for email addresses.

### On Windows
Rather than using ```./webscraper.py```
substitute that with:
```
py webscraper.py
```
followed by the domain and any additional arguments you would like to pass in.
