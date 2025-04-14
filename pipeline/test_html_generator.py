import extract


def __generate_test_html_files() -> None:
    '''DO NOT USE as it generates test html using a page whose
    values can change, making the tests obsolete'''

    url = 'https://www.goodreads.com/author/show/153394.Suzanne_Collins'
    html = extract.get_soup(url).decode()
    with open("test_author_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    url = 'https://www.goodreads.com/author/list/153394.Suzanne_Collins?page=1&per_page=100'
    html = extract.get_soup(url).decode()
    with open("test_book_list.html", "w", encoding="utf-8") as f:
        f.write(html)

    url = 'https://www.goodreads.com/book/show/2767052-the-hunger-games'
    html = extract.get_soup(url).decode()
    with open("test_book_page.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == '__main__':
    pass
