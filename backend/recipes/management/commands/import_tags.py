import csv

from django.core.management.base import BaseCommand
from tqdm import tqdm

from foodgram.settings import CSV_FILE_TAGS
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тэгов из CSV файлов'

    def handle(self, *args, **kwargs):
        Tag.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            'Все существующие ингредиенты удалены.'
        ))
        with open(CSV_FILE_TAGS,
                  'r',
                  encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            total_rows = len(rows)
            for row in tqdm(rows, total=total_rows, desc='Импорт Тэгов'):
                tags, created = Tag.objects.get_or_create(
                    name=row[0],
                    slug=row[1],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Тэг {tags.name} успешно импортирован.'
                    ))
