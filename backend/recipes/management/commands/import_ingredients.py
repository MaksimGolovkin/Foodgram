import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV файлов'

    def handle(self, *args, **kwargs):
        csv_dir = os.path.join(settings.BASE_DIR, 'data')

        with open(os.path.join(csv_dir, 'ingredients.csv'),
                  'r',
                  encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                ingredients, created = Ingredients.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Ингредиент {ingredients.name} успешно импортирован.'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Ингредиент {ingredients.name} уже существует.'
                    ))
