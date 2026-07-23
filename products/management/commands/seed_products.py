import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from products.models import Category, Product, ProductImage, Variant

SEED_MARKER = '[seed_products demo item]'

CATEGORY_WORDS = {
    'Apparel': (['Cotton', 'Slim-Fit', 'Linen', 'Wool', 'Denim', 'Classic', 'Relaxed'],
                ['Jacket', 'T-Shirt', 'Hoodie', 'Jeans', 'Sweater', 'Shorts', 'Dress']),
    'Automotive': (['Chrome', 'Heavy-Duty', 'All-Weather', 'Carbon', 'Universal', 'Premium'],
                   ['Floor Mat', 'Dash Cam', 'Car Charger', 'Seat Cover', 'Wiper Blade', 'Air Freshener']),
    'Beauty': (['Hydrating', 'Matte', 'Organic', 'Vitamin C', 'Aloe', 'Charcoal'],
               ['Face Cream', 'Lipstick', 'Shampoo', 'Serum', 'Sunscreen', 'Face Mask']),
    'Books': (['Illustrated', 'Bestselling', 'Pocket', 'Annotated', 'Collector\'s', 'Classic'],
              ['Novel', 'Cookbook', 'Biography', 'Guide', 'Journal', 'Comic']),
    'Electronics': (['Wireless', 'Smart', 'Portable', 'HD', 'Bluetooth', 'Fast-Charging'],
                    ['Headphones', 'Speaker', 'Power Bank', 'Webcam', 'Keyboard', 'Mouse', 'Charger']),
    'Groceries': (['Organic', 'Whole Grain', 'Imported', 'Fresh', 'Roasted', 'Extra Virgin'],
                  ['Coffee', 'Olive Oil', 'Pasta', 'Honey', 'Rice', 'Tea', 'Spice Mix']),
    'Home & Kitchen': (['Non-Stick', 'Stainless Steel', 'Ceramic', 'Cordless', 'Insulated', 'Compact'],
                       ['Blender', 'Cookware Set', 'Kettle', 'Cutting Board', 'Air Fryer', 'Mug']),
    'Pet Supplies': (['Grain-Free', 'Chew-Resistant', 'Washable', 'Interactive', 'Orthopedic'],
                     ['Dog Bed', 'Cat Tree', 'Pet Carrier', 'Chew Toy', 'Feeding Bowl', 'Leash']),
    'Sports & Outdoors': (['Adjustable', 'Anti-Slip', 'Lightweight', 'Waterproof', 'Foldable'],
                          ['Yoga Mat', 'Dumbbell Set', 'Camping Tent', 'Water Bottle', 'Backpack', 'Bike Helmet']),
    'Toys & Games': (['Educational', 'Glow-in-the-Dark', 'Wooden', 'Remote Control', 'Building'],
                     ['Puzzle', 'Action Figure', 'Board Game', 'Toy Car', 'Blocks Set', 'Plush Toy']),
}

CATEGORY_COLORS = {
    'Apparel': (99, 102, 241),
    'Automotive': (71, 85, 105),
    'Beauty': (236, 72, 153),
    'Books': (180, 83, 9),
    'Electronics': (14, 116, 144),
    'Groceries': (101, 163, 13),
    'Home & Kitchen': (217, 119, 6),
    'Pet Supplies': (124, 58, 237),
    'Sports & Outdoors': (5, 150, 105),
    'Toys & Games': (220, 38, 38),
}
FALLBACK_COLOR = (10, 133, 99)


def make_placeholder_image(category_name, label):
    color = CATEGORY_COLORS.get(category_name, FALLBACK_COLOR)
    img = Image.new('RGB', (600, 600), color=color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('Arial.ttf', 42)
    except OSError:
        font = ImageFont.load_default()
    text = category_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((600 - w) / 2, (600 - h) / 2), text, fill='white', font=font)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=70)
    return ContentFile(buffer.getvalue(), name=f'{label}.jpg')


class Command(BaseCommand):
    help = 'Seeds the catalog with demo products (with generated images) spread across categories, to test pagination/listing at scale.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1000, help='Number of demo products to create.')
        parser.add_argument('--clear', action='store_true', help='Delete previously seeded demo products first.')

    def handle(self, *args, **options):
        count = options['count']

        if options['clear']:
            deleted, _ = Product.objects.filter(description=SEED_MARKER).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} previously seeded rows.'))

        categories = list(Category.objects.filter(name__in=CATEGORY_WORDS.keys()))
        if not categories:
            self.stderr.write(self.style.ERROR('No matching categories found - nothing to seed against.'))
            return

        created = 0
        with transaction.atomic():
            for i in range(count):
                category = categories[i % len(categories)]
                adjectives, nouns = CATEGORY_WORDS[category.name]
                name = f'{random.choice(adjectives)} {random.choice(nouns)} #{i + 1}'
                price = random.choice([9.99, 14.5, 19.99, 24.0, 39.99, 59.5, 89.99, 129.0, 199.99])

                product = Product.objects.create(
                    category=category,
                    name=name,
                    description=SEED_MARKER,
                    price=price,
                    warranty_months=random.choice([None, None, 6, 12, 24]),
                    is_active=True,
                )

                image = ProductImage(product=product, is_primary=True, alt_text=name)
                image.image = make_placeholder_image(category.name, product.slug)
                image.save()

                Variant.objects.create(
                    product=product,
                    size=random.choice(['', 'S', 'M', 'L', 'One Size']),
                    color=random.choice(['', 'Black', 'White', 'Blue', 'Red']),
                    sku=f'SEED-{product.pk}',
                    stock=random.choice([0, 5, 10, 25, 50]),
                )

                created += 1
                if created % 100 == 0:
                    self.stdout.write(f'  ...{created}/{count}')

        self.stdout.write(self.style.SUCCESS(f'Created {created} demo products across {len(categories)} categories.'))
