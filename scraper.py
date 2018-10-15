import requests
from bs4 import BeautifulSoup
import json
import time
import random
import string
import os

from source import barsToScan
from processBars import *

DATA_DIR = 'barTextFiles/'

# For searching for bars
waitIntervals = [2, 3, 4, 5, 6, 7]
# For iterating through pages.
waitIntervalsLong = [7, 9, 12, 13, 15]


class Bar:
    def __init__(self, name):
        self.name = name


def getUserAgents():
    with open('userAgents.txt', 'r') as f:
        ua = f.readlines()
    return ua


def initializeBarInfo():
    bars = []
    for b in barsToScan:
        bar = Bar(b.lower())
        bars.append(bar)
    return bars


def getUrl(url, headers=None):
    def goodResponse(response):
        return ('html' in response.headers['Content-Type'].lower()) and \
               (response is not None) and \
               (response.status_code == 200)

    counter = 0
    while counter < 3:
        print('attempting response')
        if headers is not None:
            s = requests.Session()
            resp = s.get(url, headers=headers)
        else:
            resp = requests.get(url)
        print('response received')
        if goodResponse(resp):
            return resp
        else:
            counter += 1
            print('Bad response. Retrying {} out of 3.'.format(counter))
            print(resp.content)
            print(resp.status_code)
            time.sleep(random.choice(waitIntervals))
    return None


# Returns headers with a random user agent from a list of 100.
def getHeaders(barName, review=False, pageUrl=None):
    '''
	If used for iterating through pages of reviews, pass:
		review=True, pageUrl=url
	This will make the referer the previous page of results
	instead of Google.
	'''
    try:
        randomUserAgent = random.choice(userAgents)
        if review == True and pageUrl is not None:
            referer = pageUrl
        else:
            referer = 'https://www.google.com/search?q=yelp+' + barName
        headers = {
            'user-agent': randomUserAgent.rstrip(),
            'referer': referer,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1'
        }
    except Exception as ex:
        print('Exception in headers.')
        print(ex)
    return headers


def getYelpUrl(bars):
    def getValidation(bar, option):
        choice = input(
            'sub Is this the correct bar for {}? -- {} (Type \'y\' or \'n\' or \'q\' to quit.'.format(bar.name, option))
        bar.askedBars.append(option)
        if choice == 'n':
            pass
        elif choice == 'y':
            bar.yelpUrl = 'https://www.yelp.com' + x['href']
            bar.yelpUrl = bar.yelpUrl.split('?osq=')[0]
            print('URL recorded. ', bar.yelpUrl)
            bar.match = True
            return bar
        elif choice == 'q':
            quit()
        else:
            print('Type y or n or q only.')
        return bar

    for bar in bars:
        bar.askedBars = []
        table = str.maketrans({key: None for key in string.punctuation})
        barNameForSearch = bar.name.translate(table)
        print(barNameForSearch)
        askedBars = []
        print('Searching for {}'.format(bar.name))
        headers = getHeaders(bar.name)
        url = 'https://www.yelp.com/search?find_desc=' + bar.name + '&find_loc=Downtown,+Austin,+TX'
        counter, results = 0, []
        while len(results) == 0 and counter < 3:
            resp = getUrl(url, headers=headers)
            html = BeautifulSoup(resp.content, 'html.parser')
            results = html.find_all('a', attrs={'class': 'biz-name'})
            print('len of results is {}'.format(len(results)))
            if len(results) == 0:
                print('Retrying.')
                counter += 1
        bar.match = False
        while not bar.match:
            # First, if there is a perfect match between the bar name in source.py and the
            # bar name from the search results, auto-match it and skip user verification.
            for x in results:
                option = x.span.text.lower()
                if option == barNameForSearch:
                    bar.yelpUrl = 'https://www.yelp.com' + x['href']
                    bar.yelpUrl = bar.yelpUrl.split('?osq=')[0]
                    bar.match = True
                    print('Auto-matching {} to {}. ({})'.format(option, bar.name, bar.yelpUrl))
                    break
                else:
                    pass
            # Second, if there is a partial match, ask for verification.
            for x in results:
                if bar.match:
                    break
                option = x.span.text.lower()
                if option not in bar.askedBars:
                    if (option in barNameForSearch) or (barNameForSearch in option):
                        bar = getValidation(bar, option)
                        if bar.match:
                            break
                    else:
                        pass
            # Last, if there is no complete match or partial match, go through all results.
            for x in results:
                if bar.match:
                    break
                option = x.span.text.lower()
                if option not in askedBars:
                    bar = getValidation(bar, option)
                else:
                    pass
            waitInterval = random.choice(waitIntervals)
            print('Waiting {} seconds.'.format(waitInterval))
            print('\n\n')
            time.sleep(waitInterval)
    return bars


# writing the info we have, including Yelp url for each bar.
def writeBarsToFile(bars):
    with open('output.json', 'w') as f:
        s = json.dumps(bars, default=lambda x: x.__dict__)
        f.write(s)


def getReviews(bars):
    # Gets the number of pages of results
    def getNumberOfPages(html):
        for x in html.find_all(attrs={'class': 'page-of-pages arrange_unit arrange_unit--fill'}):
            y = (str(x.text))
            y = y.split('1 of')[1]
        return int(y)

    for b in bars:
        finalResults, midResult, pageInt, cycleNumber = [], ['a'], 0, 1
        headers = getHeaders(b.name)
        url = b.yelpUrl + '?start={}'.format(str(pageInt))
        resp = getUrl(url, headers=headers)
        html = BeautifulSoup(resp.content, 'html.parser')
        numberOfPages = getNumberOfPages(html)
        for p in range(numberOfPages):
            print('Page {} of {}.'.format(p, numberOfPages))
            url = b.yelpUrl + '?start={}'.format(str(pageInt))
            print('Attempting response from {}'.format(url))
            midResult = []
            # On first page, we already have the html from getting the page number so use
            # that instead of making a new request.
            if cycleNumber != 1:
                headers = getHeaders(b.name, review=True, pageUrl=url)
                resp = getUrl(url, headers=headers)
                html = BeautifulSoup(resp.content, 'html.parser')
            else:
                pass
            for step in html.find_all(attrs={'class': 'review-content'}):
                midResult.extend(step.find_all('p'))
            print('Appending {} reviews for {}.'.format(len(midResult), bars[i].name))
            print('First review on page: {}'.format(midResult[0].text))
            print('\n Last review on page: {} \n'.format(midResult[-1].text))
            for x in midResult:
                finalResults.append('{}\n\n'.format(x.text))
            pageInt += 20
            cycleNumber += 1
            time.sleep(random.choice(waitIntervalsLong))
        with open(os.path.join(DATA_DIR, b.name + '.txt'), 'w') as f:
            f.writelines(finalResults)


if __name__ == "__main__":
    choice = input(
        'Would you like to (1) scrape the reviews of the bars in the source file, or (2) proceed \
        to the language processing? Enter 1 or 2.')
    if choice == str(1):
        userAgents = getUserAgents()
        bars = initializeBarInfo()
        bars = getYelpUrl(bars)
        writeBarsToFile(bars)
        getReviews(bars)
        proceed = input("Would you like to proceed to language processing? y or n.".lower())
        if proceed == 'y':
            getWords()
        elif proceed == 'n':
            print('Data saved. Exiting.')
            quit()
        else:
            print('u no type good.')
    elif choice == str(2):
        getWords()
    else:
        print('u no type good.')
