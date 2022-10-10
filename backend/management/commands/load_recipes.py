import json
from os.path import split
from requests import get
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from ._parsing import save_recipes
from backend.models import Recipe, Allergy


class Command(BaseCommand):
    help = 'Loads recipes from povarenok.ru'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, action='store', help='Число рецептов для загрузки с povarenok.ru')
        parser.add_argument('-fn', '--filename', type=str, action='store', help='Имя json файла для сохранения загруженных рецептов')
        parser.add_argument('-fj', '--fromjson', type=str, action='store', help='Имя json файта для сохраннения рецептов в базу')

    def download_image(self, url, recipe):
        filename = split(url)[1]
        response = get(url)
        if not response.ok:
            self.stdout.write(self.style.WARNING(f'Image not found: {url}'))
            return
        recipe.image.save(
            filename,
            ContentFile(response.content),
            save=True
        )
        self.stdout.write(
            self.style.SUCCESS(f'Successfully retrieved image from {url}')
        )

    @transaction.atomic
    def load_recipes_to_db(self, *args, **options):
        with open(options['fromjson'], encoding='utf8') as file:
            json_recipes = json.load(file)
        for json_recipe in json_recipes:
            recipe, created = Recipe.objects.get_or_create(
                name=json_recipe['title'],
                defaults={
                    'content': "\n".join(json_recipe['instruction']),
                    'calories': json_recipe['portion_calories'],
                    'ingredients': json.dumps(json_recipe['ingredients']),
                },
            )
            if not created:
                self.stdout.write(
                    self.style.WARNING(f"Already exists:{json_recipe['title']}")
                )
                continue
            for allergen_name in json_recipe['allergens']:
                allergy, created = Allergy.objects.get_or_create(
                    name=allergen_name,
                )
                recipe.allergies.add(allergy)
            self.download_image(json_recipe['images'][0], recipe)

    def handle(self, *args, **options):
        if options['number']:
            if options['filename']:
                save_recipes(options['number'], options['filename'])
            else:
                save_recipes(options['number'])

        if not options['fromjson']:
            return
        self.load_recipes_to_db(self, *args, **options)

