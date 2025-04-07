'''This module explores extracting information from goodreads.com author pages.'''
import urllib.request
from bs4 import BeautifulSoup


TEST_AUTHOR_URL = '''https://www.goodreads.com/author/show/153394
.Suzanne_Collins?from_search=true&from_srp=true'''


def get_author_page_parser(author_url:str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com author url'''
    with urllib.request.urlopen(author_url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")

def get_author_name_from_url(url:str) -> str:
    """Gets name from goodreads.com author url and assumes url format:
    https:// ... /id.author_name or https:// ... /id.author_name?parameters"""
    start_index = url.rfind('.')+1
    name = url[start_index:]
    if "?" in name:
        end_index = name.rfind('?')
        return name[:end_index].replace("_"," ")
    return name.replace("_"," ")

def get_user_info(author_url:str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url'''
    author_soup:BeautifulSoup = get_author_page_parser(author_url)
    aggregate_contents = author_soup.find("div",class_="hreview-aggregate")

    author_name = get_author_name_from_url(author_url)
    average_rating = aggregate_contents.find("span",class_="average").text
    rating_count = aggregate_contents.find("span",class_="votes").text.strip()
    review_count = aggregate_contents.find("span",class_="count").text.strip()
    return {
        'author_name':author_name,
        'author_page':author_url,
        'average_rating':average_rating,
        'rating_count':rating_count,
        'review_count':review_count
    }


if __name__ == '__main__':
    print(get_user_info(TEST_AUTHOR_URL))
