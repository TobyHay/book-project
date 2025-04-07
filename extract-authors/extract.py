import requests
import urllib.request
from bs4 import BeautifulSoup


TEST_AUTHOR_URL = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'


def get_author_page_parser(author_url:str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com author url'''
    with urllib.request.urlopen(author_url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")

def get_user_info(author_soup:BeautifulSoup) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url'''
    aggregate_contents = author_soup.find("div",class_="hreview-aggregate")
    average_rating = aggregate_contents.find("span",class_="average").text
    rating_count = aggregate_contents.find("span",class_="votes").text.strip()
    review_count = aggregate_contents.find("span",class_="count").text.strip()
    return {
        'average_rating':average_rating,
        'rating_count':rating_count,
        'review_count':review_count
    }


if __name__ == '__main__':
    author_page_soup = get_author_page_parser(TEST_AUTHOR_URL)   
    print(get_user_info(author_page_soup))

