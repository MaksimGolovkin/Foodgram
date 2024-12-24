import csv

from django.core.management.base import BaseCommand
from tqdm import tqdm

from foodgram.settings import CSV_FILE_INGREDIENTS
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV файлов'

    def handle(self, *args, **kwargs):
        Ingredient.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            'Все существующие ингредиенты удалены.'
        ))
        with open(CSV_FILE_INGREDIENTS,
                  'r',
                  encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            total_rows = len(rows)
            for row in tqdm(
                rows, total=total_rows, desc='Импорт ингредиентов'
            ):
                ingredients, created = Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Ингредиент {ingredients.name} успешно импортирован.'
                    ))
