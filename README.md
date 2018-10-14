# yelp-review-scraper
Scraping yelp reviews of local bars for future use.

First, edit the source.py file with the list of bar names you'd like to scrape.

If using outside of downtown Austin, some urls in the scraper.py file need to be edited.

The script will:
1. Pull the list of bars to search and then have the user confirm the correct match.
2. Get all reviews for each bar and write to a .txt file titled with the name of the bar.

Most of the script is designed to avoid getting your IP address blacklisted from Yelp: random wait intervals, 
random User Agent, referers, etc.

To run, download, edit the source.py file, and then run `python3 scraper.py`.
