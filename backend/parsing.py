import argparse
import json
from itertools import chain
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urljoin, urlsplit
import random

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

PAGES_QUANTITY = 10000


def check_for_page_redirect(response: requests.Response, page):
    if response.history:
        err_msg = f'There is no page {page}'
        raise requests.HTTPError(err_msg)


def get_one_page_recipe_ids(genre_url: str, page: int) -> list:
    page_url = f'{genre_url}~{page}/'
    response = requests.get(page_url)
    response.raise_for_status()
    check_for_page_redirect(response, page)
    soup = BeautifulSoup(response.text, 'lxml')
    return [book.select_one('h2').select_one('a')['href'].strip('/b')
            for book in soup.select('body article.item-bl')]


def main():
    recipes_url = 'https://www.povarenok.ru/recipes/'
    random_page = random.choice(range(2, PAGES_QUANTITY))

    print(get_one_page_recipe_ids(recipes_url, random_page))


if __name__ == '__main__':
    main()
