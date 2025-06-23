# Management Commands
# management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from accounts.models import DeliveryPerson
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for MzBell\'s Bakery'
    
    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Cakes', 'description': 'Delicious birthday cakes, wedding cakes, and custom cakes'},
            {'name': 'Breads', 'description': 'Fresh baked breads and rolls'},
            {'name': 'Pastries', 'description': 'Sweet and savory pastries'},
            {'name': 'Cookies', 'description': 'Homemade cookies and biscuits'},
            {'name': 'Cupcakes', 'description': 'Individual cupcakes for any occasion'},
            {'name': 'Pies', 'description': 'Traditional pies and tarts'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample products
        products_data = [
            # Cakes
            {'name': 'Chocolate Birthday Cake', 'category': 'Cakes', 'price': '45.00', 'description': 'Rich chocolate cake perfect for birthdays', 'prep_time': 120},
            {'name': 'Vanilla Wedding Cake', 'category': 'Cakes', 'price': '120.00', 'description': 'Elegant 3-tier vanilla wedding cake', 'prep_time': 240},
            {'name': 'Red Velvet Cake', 'category': 'Cakes', 'price': '55.00', 'description': 'Classic red velvet with cream cheese frosting', 'prep_time': 150},
            
            # Breads
            {'name': 'Sourdough Bread', 'category': 'Breads', 'price': '12.00', 'description': 'Artisan sourdough bread', 'prep_time': 60},
            {'name': 'Whole Wheat Bread', 'category': 'Breads', 'price': '10.00', 'description': 'Healthy whole wheat bread', 'prep_time': 45},
            {'name': 'French Baguette', 'category': 'Breads', 'price': '8.00', 'description': 'Traditional French baguette', 'prep_time': 30},
            
            # Pastries
            {'name': 'Croissants', 'category': 'Pastries', 'price': '15.00', 'description': 'Buttery, flaky croissants (pack of 6)', 'prep_time': 90},
            {'name': 'Danish Pastries', 'category': 'Pastries', 'price': '18.00', 'description': 'Assorted Danish pastries (pack of 4)', 'prep_time': 75},
            {'name': 'Meat Pies', 'category': 'Pastries', 'price': '25.00', 'description': 'Savory meat pies (pack of 6)', 'prep_time': 60},
            
            # Cookies
            {'name': 'Chocolate Chip Cookies', 'category': 'Cookies', 'price': '20.00', 'description': 'Classic chocolate chip cookies (dozen)', 'prep_time': 30},
            {'name': 'Oatmeal Cookies', 'category': 'Cookies', 'price': '18.00', 'description': 'Healthy oatmeal cookies (dozen)', 'prep_time': 25},
            
            # Cupcakes
            {'name': 'Vanilla Cupcakes', 'category': 'Cupcakes', 'price': '24.00', 'description': 'Vanilla cupcakes with buttercream (dozen)', 'prep_time': 45},
            {'name': 'Chocolate Cupcakes', 'category': 'Cupcakes', 'price': '26.00', 'description': 'Chocolate cupcakes with chocolate frosting (dozen)', 'prep_time': 45},
        ]
        
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': prod_data['description'],
                    'category': category,
                    'price': Decimal(prod_data['price']),
                    'preparation_time': prod_data['prep_time'],
                    'stock_quantity': 50,
                    'is_available': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@mzbellsbakery.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                phone_number='+233201234567'
            )
            self.stdout.write('Created admin user: admin/admin123')
        
        # Create sample delivery person
        if not User.objects.filter(username='delivery1').exists():
            delivery_user = User.objects.create_user(
                username='delivery1',
                email='delivery@mzbellsbakery.com',
                password='delivery123',
                first_name='John',
                last_name='Delivery',
                phone_number='+233207654321',
                is_delivery_person=True
            )
            
            DeliveryPerson.objects.create(
                user=delivery_user,
                vehicle_type='bike',
                license_number='DL123456',
                is_available=True
            )
            self.stdout.write('Created delivery person: delivery1/delivery123')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))