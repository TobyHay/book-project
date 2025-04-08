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


def get_book_small_image_url(book_soup:BeautifulSoup) -> str:
    '''Gets the url from the soup of an individual 
    book container from the author's book list '''
    return book_soup.find('img').get('src')


def get_book_title(book_soup:BeautifulSoup) -> str:
    '''Gets the book title from the soup of an individual 
    book container from the author's book list '''
    return book_soup.find('span',itemprop="name").text


def slice_book_average_rating(aggregate_text:str) -> str:
    '''Gets a book's average rating from the
      author's books list page's aggregate data grey text''' # rephrase pls :,)
    slice_index = aggregate_text.find('avg')
    return aggregate_text[:slice_index-1]


def slice_book_rating_count(aggregate_text:str) -> str:
    '''Gets a book's rating count from the
      author's books list page's aggregate data grey text''' # rephrase pls :,)
    start_slice_index = aggregate_text.find('—')+2 # magic number 
    end_slice_index = aggregate_text.rfind('r')-1 # magic number 
    return aggregate_text[start_slice_index:end_slice_index]
    

def get_book_aggregate_data(book_soup:BeautifulSoup) -> dict:
    '''Given a book card's html in the goodreads author's book list,
      scrape all aggregate data for the given book'''
    avg_and_rating = book_soup.find('span',class_='minirating').text
    return {
        'avg_rating':slice_book_average_rating(avg_and_rating),
        'rating_count':slice_book_average_rating(avg_and_rating)
    }
    

def get_year_published(book_soup:BeautifulSoup) -> dict:
    '''gets year published from a '''
    year_published = book_soup.find('span',class_='greyText smallText uitext').text
    return year_published.split()[-4] # magic number 


def get_individual_book_data(book_soup:BeautifulSoup) -> dict:
    '''Book.'''  #rewrite
    book_data = {
        'book_title':get_book_title(book_soup),
        'small_image_url':get_book_small_image_url(book_soup),
        'year_published':get_year_published(book_soup)
    }
    book_data.update(get_book_aggregate_data(book_soup))
    return book_data


def get_author_books(books_list_soup:BeautifulSoup) -> list[dict]:
    '''gets a list of all books in a author's goodreads book list'''
    scraped_books = books_list_soup.find_all("tr")
    formatted_books = []
    for book in scraped_books:
        formatted_books.append(get_individual_book_data(book))
    return formatted_books


def get_shelved_books_count(books_list_soup:BeautifulSoup) -> str:
    '''Returns the shelved count for all of an author's books.'''
    shelved_count = books_list_soup.find('div',class_='leftContainer')
    shelved_count = shelved_count.find_next('div').text
    return shelved_count.split()[-2] # Magic number


def get_author_image(author_soup:BeautifulSoup) -> dict:
    '''Gets the author image from the author's goodread page.'''
    return author_soup.find('img',itemprop="image").get('src')


def get_authors_book_list_data(author_soup:BeautifulSoup) -> dict:
    ''''''
    books_url = get_authors_books_url(author_soup)
    books_soup = get_soup(books_url)

    books_data = {'shelved_count':get_shelved_books_count(books_soup),
                  'author_image':get_author_image(author_soup),
                  'books':get_author_books(books_soup)}
    return books_data


def get_author_data(author_url:str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url.'''
    author_soup:BeautifulSoup = get_soup(author_url)
    
    author_name = get_author_name(author_soup)
    aggregate_data = get_author_aggregate_data(author_soup)

    books_data = get_authors_book_list_data(author_soup)

    author_data = {
        'author_name':author_name,
        'author_url':author_url
    }
    author_data.update(aggregate_data)
    author_data.update(books_data)
    return author_data


if __name__ == '__main__':
    author_url = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'

    print(get_author_data(author_url))