import csv
import os
from django.core.management.base import BaseCommand
from ratings.models import Rating
from config.settings import BASE_DIR
from django_common.utils.isbn_helpers import *

class Command(BaseCommand):
    help = 'Import ratings from ratings.csv'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(BASE_DIR, 'data/ratings.csv')

        self.stdout.write(f'Loading ratings from {file_path}')

        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            ratings = []
            for row in reader:
                try:
                    rating = row['Book-Rating']
                    isbn = clean_isbn(row['ISBN'])
                    
                    if not is_valid_isbn(isbn):
                        self.stderr.write(f"Skipping row: invalid ISBN {isbn}")
                        continue
                    
                    if rating.isdigit() and int(rating) != 0:
                        ratings.append(Rating(
                            user_id=int(row['User-ID']),
                            isbn=isbn,
                            rating=int(rating),
                        ))
                except Exception as e:
                    self.stderr.write(f"Skipping row due to error: {e}")
            
            if ratings:
                Rating.objects.bulk_create(ratings, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported {len(ratings)} ratings'
                ))
            else:
                self.stdout.write(self.style.WARNING('No valid ratings to import'))
