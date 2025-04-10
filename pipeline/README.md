# Overview

This module focuses on extracting author information and contains the following scripts:
- Note: All mention of soup in the following scripts does not refer to the liquid food referred to as soup, but rather refers to a BeautifulSoup object from the [bs4 libraryy](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), which is an abstracted, highly parsable version of the html for the specified url.
- `extract.py` : Extracts author information for the specified author goodreads url specified in the code. The returned data is in the following form:
```
{
    'author_name':author_name,
    'author_page':author_url,
    'average_rating':average_rating,
    'rating_count':rating_count,
    'review_count':review_count,
    'shelved_count': get_shelved_books_count(books_soup),
    'author_image': get_author_image(author_soup),
    'book':[{
        'book_title':book_title,
        'book_url': book_url,
        'big_image_url':big_image_url,
        'small_image_url':small_image_url,
        'review_count':review_count,
        'year_published': year_published
    }]
}
```


# Pre-requisites

- `pip install -r requirements.txt`.
- Specify an author as a parameter for get_user_info() (SUBJECT TO CHANGE WHEN COORDINATING THE ETL STAGES)


# Usage

- SUBJECT TO CHANGE WHEN COORDINATING THE ETL STAGES



# IMPORTANT 

- `test_html_generator.py`: 
-  Note: Do not use this!!
-  This is used to generate the mock htmls for testing and generating them again could cause the values to change, making the tests obsolete.