import csv
import os
from django.core.management.base import BaseCommand
from ratings.models import Rating
from config.settings import BASE_DIR

class Command(BaseCommand):
    help = 'Import ratings from ratings.csv'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(BASE_DIR, 'data/ratings.csv')

        self.stdout.write(f'Loading ratings from {file_path}')

        def clean_isbn(isbn: str) -> str:
            """Remove spaces, quotes, and hyphens from ISBN."""
            return isbn.replace('-', '').replace(' ', '').replace('"', '').strip()

        def is_valid_isbn10(isbn: str) -> bool:
            """Check if ISBN-10 is valid."""
            if len(isbn) != 10 or not isbn[:-1].isdigit():
                return False
            total = sum((i + 1) * int(x) for i, x in enumerate(isbn[:-1]))
            check = isbn[-1]
            if check.upper() == 'X':
                total += 10 * 10
            elif check.isdigit():
                total += 10 * int(check)
            else:
                return False
            return total % 11 == 0

        def is_valid_isbn13(isbn: str) -> bool:
            """Check if ISBN-13 is valid."""
            if len(isbn) != 13 or not isbn.isdigit():
                return False
            total = sum((int(num) * (1 if i % 2 == 0 else 3)) for i, num in enumerate(isbn[:-1]))
            check_digit = (10 - (total % 10)) % 10
            return check_digit == int(isbn[-1])

        def is_valid_isbn(isbn: str) -> bool:
            """Validate ISBN-10 or ISBN-13."""
            isbn = clean_isbn(isbn)
            return is_valid_isbn10(isbn) or is_valid_isbn13(isbn)

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
