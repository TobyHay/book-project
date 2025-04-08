'''This module explores extracting information from goodreads.com author pages.'''
import urllib.request
from bs4 import BeautifulSoup



def get_author_page_parser(author_url:str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com author url.'''
    with urllib.request.urlopen(author_url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")


def get_author_name_from_url(url:str) -> dict:
    """Gets name from goodreads.com author url and assumes url format:
    https:// ... /id.author_name or https:// ... /id.author_name?parameters"""
    start_index = url.rfind('.')+1
    name = url[start_index:]
    if "?" in name:
        end_index = name.rfind('?')
        return {'author_name':name[:end_index].replace("_"," ")}
    return {'author_name':name.replace("_"," ")}


def get_author_name_from_soup(soup:BeautifulSoup) -> dict:
    '''gets author name from the soup for the author goodreads page'''
    pass


def get_author_aggregate_data(author_soup:BeautifulSoup) -> dict:
    '''Uses the soup from the author page to get aggregate 
    values about the author such as average ratings for all books.'''
    aggregate_contents = author_soup.find("div",class_="hreview-aggregate")
    average_rating = aggregate_contents.find("span",class_="average").text
    rating_count = aggregate_contents.find("span",class_="votes").text.strip()
    review_count = aggregate_contents.find("span",class_="count").text.strip()

    # goodreads_followers = NotImplementedError

    shelved_count = author_soup.find("div",class_="h2Container gradientHeaderContainer")
    print(shelved_count.prettify())
    
    
    
    raise NotImplementedError
    return {
        'average_rating':average_rating,
        'rating_count':rating_count,
        'review_count':review_count,
        'shelved_count':shelved_count,
        'goodreads_followers':goodreads_followers
    }


def get_authors_books_url(author_soup:BeautifulSoup) -> str:
    '''Gets the link to the author's books from their goodreads profile'''
    author_soup.find("a",class_="hreview-aggregate")


def get_book_aggregate_data(author_soup:BeautifulSoup) ->dict:
    '''Given a book card's html in the goodreads author's book list,
      scrape all aggregate data for the given card'''


def get_authors_books(author_soup:BeautifulSoup) -> dict:
    ''''''
    books = {'books':[]}
    return 

def get_user_info(author_url:str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url.'''
    author_soup:BeautifulSoup = get_author_page_parser(author_url)
    
    author_name = get_author_name_from_url(author_url)
    aggregate_data = get_author_aggregate_data(author_soup)

    author_info = {
        'author_name':author_name,
        'author_page':author_url,
    }
    return author_info + aggregate_data


if __name__ == '__main__':
    print(get_user_info('''https://www.goodreads.com/author/show/153394
.Suzanne_Collins?from_search=true&from_srp=true'''))
