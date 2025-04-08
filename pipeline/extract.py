'''This module explores extracting information from goodreads.com author pages.'''
import urllib.request
from bs4 import BeautifulSoup

GOODREADS_BASE_URL = 'https://www.goodreads.com'
BOOKS_LIST_LIMIT_URL_PARAMETERS = '?page=1&per_page=100'


def get_soup(url:str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com url.'''
    with urllib.request.urlopen(url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")


def get_authors_books_url(author_soup:BeautifulSoup) -> str:
    '''Gets the link to the author's books list from their goodreads profile'''
    books_url = author_soup.find("a",string='Suzanne Collins’s books')
    return GOODREADS_BASE_URL + books_url.get('href') + BOOKS_LIST_LIMIT_URL_PARAMETERS


def get_author_name(author_soup:BeautifulSoup) -> dict:
    '''gets author name from the soup for the author goodreads page'''
    author_name = author_soup.find("h1",class_="authorName").text
    return author_name.strip()


def get_author_follower_count(author_soup:BeautifulSoup) -> str:
    '''Gets the authors follower count from their goodreads author page soup '''
    follower_count = author_soup.find("div",class_="h2Container gradientHeaderContainer")
    follower_count = follower_count.find("h2",class_="brownBackground").text

    start_index = follower_count.rfind('(')+1
    end_index = len(follower_count)-1
    return follower_count[start_index:end_index]


def get_author_aggregate_data(author_soup:BeautifulSoup) -> dict:
    '''Uses the soup from the author page to get aggregate 
    values about the author such as average ratings for all books.'''
    aggregate_contents = author_soup.find("div",class_="hreview-aggregate")
    average_rating = aggregate_contents.find("span",class_="average").text
    rating_count = aggregate_contents.find("span",class_="votes").text.strip()
    review_count = aggregate_contents.find("span",class_="count").text.strip()
    followers = get_author_follower_count(author_soup)

    return {
        'average_rating':average_rating,
        'rating_count':rating_count,
        'review_count':review_count,
        'goodreads_followers':followers
    }


def get_book_aggregate_data(author_soup:BeautifulSoup) ->dict:
    '''Given a book card's html in the goodreads author's book list,
      scrape all aggregate data for the given card'''


def get_authors_books(author_soup:BeautifulSoup) -> dict:
    ''''''
    shelved_count = NotImplementedError
    books = {'shelved_count':shelved_count,'books':[]}
    return 

def get_author_data(author_url:str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url.'''
    author_soup:BeautifulSoup = get_soup(author_url)
    
    author_name = get_author_name(author_soup)
    aggregate_data = get_author_aggregate_data(author_soup)

    author_data = {
        'author_name':author_name,
        'author_page':author_url
    }
    author_data.update(aggregate_data)
    return author_data

def get_author_image():
    pass

def get_book_image():
    pass

def get_book_list_data():
    pass




if __name__ == '__main__':
    url = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'
    suzanne_soup = get_soup(
        'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'
        )
    print(get_author_data(url))