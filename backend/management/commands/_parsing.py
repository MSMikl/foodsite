import argparse
import json
import os
import random
from pathlib import Path
from django.conf import settings

import requests
from bs4 import BeautifulSoup


def check_for_page_redirect(response: requests.Response, page):
    if response.history:
        err_msg = f'There is no page {page}'
        raise requests.HTTPError(err_msg)


def save_pretty_json(data, filename: str):
    # json_path = Path(path)
    # json_path.mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(settings.STATIC_ROOT, filename)
    with open(file_path, 'w', encoding='utf8') as file:
        file.write(json.dumps(data, indent=4, ensure_ascii=False))


def get_recipe_title(recipe_soup: BeautifulSoup) -> str:
    title_soup = recipe_soup.select_one(
        'article.item-bl.item-about div h1'
    )
    if not title_soup:
        return None
    return title_soup.text


def get_recipe_ingredients(recipe_soup: BeautifulSoup) -> str:
    c1 = 'article.item-bl.item-about'
    c2 = 'div div.ingredients-bl ul li'
    ingredients_soup = recipe_soup.select(f'{c1} {c2}')
    if not ingredients_soup:
        return None
    ingredients = '\n'.join(
        ' '.join(x.text.replace('\n', '').split())
        for x in ingredients_soup
    )
    if not ingredients:
        return None
    if not ingredients.replace('\n', ''):
        return None
    return ingredients


def get_recipe_instruction(recipe_soup: BeautifulSoup) -> str:
    c1 = 'article.item-bl.item-about div'
    c2 = 'ul li.cooking-bl div p'
    instruction_soup = recipe_soup.select(f'{c1} {c2}')
    if not instruction_soup:
        return None
    instruction = '\n'.join(
        x.text
        for x in instruction_soup
    )
    if not instruction:
        return None
    if not instruction.replace('\n', ''):
        return None
    return instruction


def get_portion_calories(recipe_soup: BeautifulSoup) -> float:
    c1 = 'body article.item-bl.item-about div'
    c2 = 'div#nae-value-bl div table tr td strong'
    nutrition_tags = recipe_soup.select(f'{c1} {c2}')
    if not nutrition_tags:
        return None
    portion = nutrition_tags[5].text
    calories = float(nutrition_tags[6].text.strip(' ккал'))
    if 'Порции' not in portion:
        return calories * 2.0
    return calories


def get_images_urls(recipe_soup: BeautifulSoup) -> list:
    def_img = 'https://www.povarenok.ru/images/recipes/1.gif'
    title_img_soup = recipe_soup.select_one('div.m-img img')
    if not title_img_soup:
        return None
    title_img = title_img_soup['src']
    if title_img == def_img:
        return None
    images = []
    images.append(title_img)
    c1 = 'body article.item-bl.item-about div'
    c2 = 'ul li.cooking-bl span.cook-img a img'
    cook_imgs = recipe_soup.select(f'{c1} {c2}')
    if not cook_imgs:
        return None
    images.extend(x['src'] for x in cook_imgs)
    return images


def parse_recipe_page(recipe_url: str):
    response = requests.get(recipe_url)
    response.raise_for_status()
    recipe_soup = BeautifulSoup(response.text, 'lxml')
    parsed_recipe = {
        'title': get_recipe_title(recipe_soup),
        'ingredients': get_recipe_ingredients(recipe_soup),
        'instruction': get_recipe_instruction(recipe_soup),
        'portion_calories': get_portion_calories(recipe_soup),
        'images': get_images_urls(recipe_soup),
    }
    if None in parsed_recipe.values():
        return None
    return parsed_recipe


def get_recipe_urls(page: int) -> list:
    recipes_url = 'https://www.povarenok.ru/recipes/'
    page_url = f'{recipes_url}~{page}/'
    response = requests.get(page_url)
    response.raise_for_status()
    check_for_page_redirect(response, page)
    soup = BeautifulSoup(response.text, 'lxml')
    return [book.select_one('h2').select_one('a')['href'].strip('/b')
            for book in soup.select('body article.item-bl')]


def get_parsed_recipes(number: int) -> list:
    START_PAGE = 2  # to avoid redirect
    PAGES_QUANTITY = 10000
    RECIPES_IN_ONE_PAGE = 15
    number_of_pages = int(number / RECIPES_IN_ONE_PAGE) + 1
    random_pages = random.sample(
        population=range(START_PAGE, PAGES_QUANTITY),
        k=number_of_pages
    )
    parsed_recipes = []
    for page in random_pages:
        for url in get_recipe_urls(page):
            if len(parsed_recipes) >= number:
                break
            parsed_recipe = parse_recipe_page(url)
            if not parsed_recipe:
                continue
            parsed_recipes.append(parsed_recipe)
    return parsed_recipes


def save_recipes(number: int, filename: str='recipes.json'):
    if not filename.endswith('.json'):
        filename += '.json'
    save_pretty_json(get_parsed_recipes(number), filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--number', type=int, default=20)
    args = parser.parse_args()
    save_recipes(args.number)


if __name__ == '__main__':
    main()
