import json
from os.path import split
from marshmallow import ValidationError
from requests import get
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from ._parsing import save_recipes
from backend.models import Recipe


class Command(BaseCommand):
    help = 'Loads recipes from povarenok.ru'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, action='store')
        parser.add_argument('-fn', '--filename', type=str, action='store')
        parser.add_argument('-fj', '--fromjson', type=str, action='store')

    def download_image(self, url, recipe):
        filename = split(url)[1]
        response = get(url)
        if not response.ok:
            self.stdout.write(self.style.WARNING(f'Image not found: {url}'))
            return
        recipe.picture.save(
            filename,
            ContentFile(response.content),
            save=True
        )
        self.stdout.write(
            self.style.SUCCESS(f'Successfully retrieved image from {url}')
        )

    def handle(self, *args, **options):
        if options['number']:
            if options['filename']:
                save_recipes(options['number'], options['filename'])
            else:
                save_recipes(options['number'])

        if not options['fromjson']:
            return
        with open(options['fromjson'], encoding='utf8') as file:
            json_recipes = json.load(file)
        for json_recipe in json_recipes:
            recipe, created = Recipe.objects.get_or_create(
                name=json_recipe['title'],
                defaults={
                    'content': json_recipe['instruction'],
                    'calories': json_recipe['portion_calories'],
                    'ingredients': json.dumps(json_recipe['ingredients']),
                },
            )
            if not created:
                self.stdout.write(
                    self.style.WARNING(f"Already exists:{json_recipe['title']}")
                )
                continue
            self.download_image(json_recipe['images'][0], recipe)
