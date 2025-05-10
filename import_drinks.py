import os
import django
import csv
from decimal import Decimal, InvalidOperation

# Setup Django environment for standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lovebeer.settings')
django.setup()

from lovedrinks.models import drinks

csv_path = 'all_cleaned_drinks.csv'
count = 0
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        abv = row['drink_abv']
        try:
            abv = Decimal(abv) if abv else Decimal('0.00')
        except InvalidOperation:
            abv = Decimal('0.00')
        drink = drinks(
            drink_name=row['drink_name'],
            drink_type=row['drink_type'],
            drink_image=None,  # Set a default if you want
            drink_abv=abv,
            drink_producer=row['drink_producer'],
            drink_tasting_notes=row['drink_tasting_notes'],
        )
        drink.save()
        count += 1
print(f'Successfully imported {count} drinks.') 