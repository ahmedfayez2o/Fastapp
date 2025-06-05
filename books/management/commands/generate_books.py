from django.core.management.base import BaseCommand
from books.models import Book
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Generate sample books for testing'

    def handle(self, *args, **kwargs):
        # Sample book data
        books_data = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'publisher': 'Scribner',
                'publication_year': 1925,
                'price': Decimal('14.99'),
                'stock_quantity': 20,
                'description': 'A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.'
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780446310789',
                'publisher': 'Grand Central Publishing',
                'publication_year': 1960,
                'price': Decimal('12.99'),
                'stock_quantity': 15,
                'description': 'The story of racial injustice and the loss of innocence in the American South.'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'publisher': 'Signet Classic',
                'publication_year': 1949,
                'price': Decimal('9.99'),
                'stock_quantity': 25,
                'description': 'A dystopian novel set in a totalitarian society.'
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'publisher': 'Penguin Classics',
                'publication_year': 1813,
                'price': Decimal('7.99'),
                'stock_quantity': 18,
                'description': 'A romantic novel of manners.'
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'isbn': '9780316769488',
                'publisher': 'Little, Brown and Company',
                'publication_year': 1951,
                'price': Decimal('11.99'),
                'stock_quantity': 22,
                'description': 'A classic coming-of-age story.'
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780547928227',
                'publisher': 'Mariner Books',
                'publication_year': 1937,
                'price': Decimal('15.99'),
                'stock_quantity': 30,
                'description': 'A fantasy novel about the adventures of Bilbo Baggins.'
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'isbn': '9780062315007',
                'publisher': 'HarperOne',
                'publication_year': 1988,
                'price': Decimal('13.99'),
                'stock_quantity': 17,
                'description': 'A philosophical novel about a young shepherd on a journey to find his personal legend.'
            },
            {
                'title': 'The Little Prince',
                'author': 'Antoine de Saint-Exupéry',
                'isbn': '9780156013987',
                'publisher': 'Mariner Books',
                'publication_year': 1943,
                'price': Decimal('8.99'),
                'stock_quantity': 28,
                'description': 'A poetic tale about a young prince who visits various planets in space.'
            },
            {
                'title': 'The Da Vinci Code',
                'author': 'Dan Brown',
                'isbn': '9780307474278',
                'publisher': 'Anchor',
                'publication_year': 2003,
                'price': Decimal('16.99'),
                'stock_quantity': 35,
                'description': 'A mystery thriller novel.'
            },
            {
                'title': 'The Kite Runner',
                'author': 'Khaled Hosseini',
                'isbn': '9781594631931',
                'publisher': 'Riverhead Books',
                'publication_year': 2003,
                'price': Decimal('14.99'),
                'stock_quantity': 24,
                'description': 'A story of friendship, betrayal, and redemption.'
            }
        ]

        books_created = 0
        books_updated = 0

        for book_data in books_data:
            book, created = Book.objects.update_or_create(
                isbn=book_data['isbn'],
                defaults=book_data
            )
            
            if created:
                books_created += 1
            else:
                books_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed books. Created: {books_created}, Updated: {books_updated}'
            )
        ) 