import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Tags


class Command(BaseCommand):
    help = 'Импорт тэгов из CSV файлов'

    def handle(self, *args, **kwargs):
        csv_dir = os.path.join(settings.BASE_DIR, 'data')

        with open(os.path.join(csv_dir, 'tags.csv'),
                  'r',
                  encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                tags, created = Tags.objects.get_or_create(
                    name=row[0],
                    slug=row[1],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Тэг {tags.name} успешно импортирован.'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Тэг {tags.name} уже существует.'
                    ))
