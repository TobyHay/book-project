'''This module explores extracting information from goodreads.com author pages.'''
import time
import urllib.request
from bs4 import BeautifulSoup

GOODREADS_BASE_URL = 'https://www.goodreads.com'
BOOKS_LIST_LIMIT_URL_PARAMETERS = '?page=1&per_page=10'


def get_soup(url: str) -> BeautifulSoup:
    '''Returns a beautifulsoup HTML parser for a given goodreads.com url.'''
    with urllib.request.urlopen(url) as page:
        html = page.read().decode('utf-8')
    return BeautifulSoup(html, "lxml")


def get_authors_books_url(author_soup: BeautifulSoup) -> str:
    '''Gets the link to the author's books list from their goodreads profile'''
    books_url = author_soup.find("a", href=lambda x: x and '/author/list' in x)
    return GOODREADS_BASE_URL + books_url.get('href') + BOOKS_LIST_LIMIT_URL_PARAMETERS


def get_author_name(author_soup: BeautifulSoup) -> dict:
    '''gets author name from the soup for the author goodreads page'''
    author_name = author_soup.find("h1", class_="authorName").text
    return author_name.strip()


def get_author_follower_count(author_soup: BeautifulSoup) -> str:
    '''Gets the authors follower count from their goodreads author page soup '''
    follower_count = author_soup.find(
        "div", class_="h2Container gradientHeaderContainer")
    follower_count = follower_count.find("h2", class_="brownBackground").text

    start_index = follower_count.rfind('(')+1
    end_index = len(follower_count)-1
    return follower_count[start_index:end_index]


def get_author_aggregate_data(author_soup: BeautifulSoup) -> dict:
    '''Uses the soup from the author page to get aggregate 
    values about the author such as average ratings for all books.'''
    aggregate_contents = author_soup.find("div", class_="hreview-aggregate")
    average_rating = aggregate_contents.find("span", class_="average").text
    rating_count = aggregate_contents.find("span", class_="votes").text.strip()
    review_count = aggregate_contents.find("span", class_="count").text.strip()
    followers = get_author_follower_count(author_soup)
    return {
        'average_rating': average_rating,
        'rating_count': rating_count,
        'review_count': review_count,
        'goodreads_followers': followers
    }


def get_book_small_image_url(book_container_soup: BeautifulSoup) -> str:
    '''Gets the url from the soup of an individual 
    book container from the author's book list '''
    return book_container_soup.find('img', class_='bookCover').get('src')


def get_book_title(book_container_soup: BeautifulSoup) -> str:
    '''Gets the book title from the soup of an individual 
    book container from the author's book list '''
    return book_container_soup.find('span', itemprop="name").text


def slice_book_average_rating(aggregate_text: str) -> str:
    '''Gets a book's average rating from the aggregate data's grey 
    text from a single book html container in author's books list pages '''
    slice_index = aggregate_text.find('avg')
    return aggregate_text[:slice_index-1]


def slice_book_rating_count(aggregate_text: str) -> str:
    '''Gets a book's rating count from the aggregate data's grey 
    text from a single book html container in author's books list pages '''
    start_slice_index = aggregate_text.find('—')+2
    end_slice_index = aggregate_text.rfind('r')-1
    return aggregate_text[start_slice_index:end_slice_index]


def get_book_aggregate_data(book_container_soup: BeautifulSoup) -> dict:
    '''Given a book card's html in the goodreads author's book list,
      scrape all aggregate data for the given book'''
    average_book_rating_and_rating_count = book_container_soup.find(
        'span', class_='minirating').text
    return {
        'average_rating': slice_book_average_rating(average_book_rating_and_rating_count),
        'rating_count': slice_book_rating_count(average_book_rating_and_rating_count)
    }


def get_year_published(book_container_soup: BeautifulSoup) -> dict:
    '''gets year published from a html container 
    for a book from the book list html'''
    year_published = book_container_soup.find(
        'span', class_='greyText smallText uitext').text
    return year_published.split()[-4]  # magic number?


def get_individual_book_data(book_container_soup: BeautifulSoup) -> dict:
    '''Gets information about an individual book from its container in the authors
    book list page and the book's individual page.'''
    book_url = get_book_url(book_container_soup)
    book_page_soup = get_soup(book_url)
    book_data = {
        'book_title': get_book_title(book_container_soup),
        'book_url_path': book_url,
        'big_image_url': get_book_big_image_url(book_page_soup),
        'small_image_url': get_book_small_image_url(book_container_soup),
        'review_count': get_book_review_count(book_page_soup),
        'year_published': get_year_published(book_container_soup)
    }
    aggregate_data: dict = get_book_aggregate_data(book_container_soup)
    book_data.update(aggregate_data)
    return book_data


def get_authors_books(books_list_soup: BeautifulSoup) -> list[dict]:
    '''gets a list of all books in a author's goodreads book list'''
    scraped_books = books_list_soup.find_all("tr")
    formatted_books = []
    for book in scraped_books:
        formatted_books.append(get_individual_book_data(book))
        print(f"Book scraped")
    return formatted_books


def get_shelved_books_count(books_list_soup: BeautifulSoup) -> str:
    '''Returns the shelved count for all of an author's books.'''
    shelved_count = books_list_soup.find('div', class_='leftContainer')
    shelved_count = shelved_count.find_next('div').text
    return shelved_count.split()[-2]


def get_author_image(author_soup: BeautifulSoup) -> dict:
    '''Gets the author image from the author's goodread page.'''
    return author_soup.find('img', itemprop="image").get('src')


def get_authors_books_measurement_data(author_soup: BeautifulSoup) -> dict:
    '''Gets data from the author's book list page, including book information,
    shelved books count and the author's image.'''
    books_url = get_authors_books_url(author_soup)
    books_soup = get_soup(books_url)

    books_data = {'shelved_count': get_shelved_books_count(books_soup),
                  'author_image_url': get_author_image(author_soup),
                  'books': get_authors_books(books_soup)}
    return books_data


def get_author_data(author_url: str) -> dict:
    '''Scrapes average_rating, rating_count and review_count
      for a given goodreads.com author url.'''
    author_soup: BeautifulSoup = get_soup(author_url)

    author_name = get_author_name(author_soup)

    aggregate_data: dict = get_author_aggregate_data(author_soup)
    books_data: dict = get_authors_books_measurement_data(author_soup)
    author_data = {
        'author_name': author_name,
        'author_url': author_url
    }
    author_data.update(aggregate_data)
    author_data.update(books_data)
    return author_data


def get_book_url(book_list_container_soup: BeautifulSoup) -> str:
    '''Gets book url from the soup of an html container for a book
    in a book list page'''
    book_url_path = book_list_container_soup.find('a', itemprop='url')
    book_url_path = book_url_path.get('href')
    return GOODREADS_BASE_URL + book_url_path


def get_book_big_image_url(book_soup: BeautifulSoup) -> str:
    '''gets a big image from the html of a given book page'''
    image_url = book_soup.find('div', class_='BookCover__image')
    return image_url.find('img').get('src')


def get_book_review_count(book_soup: BeautifulSoup) -> str:
    '''gets the review count of a book in the html of a given book page'''
    review_count = book_soup.find(
        'div', class_='RatingStatistics__meta').get('aria-label')
    slice_index_start = review_count.rfind('d')+2
    slice_index_end = review_count.rfind('reviews')-1
    return review_count[slice_index_start:slice_index_end]


if __name__ == '__main__':
    author_url = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins?from_search=true&from_srp=true'

    start_time = time.time()
    print(get_author_data(author_url))
    print('time:', time.time()-start_time)
