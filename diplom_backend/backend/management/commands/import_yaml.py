import yaml
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductParameter

class Command(BaseCommand):
    help = 'Import data from YAML file'
    
    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='YAML file to import')

    def handle(self, *args, **options):
          
        with open(options['filename'], 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Создание или получение магазина
        shop, created = Shop.objects.get_or_create(name=data['shop'])
        
        # Импорт категорий
        category_map = {}
        for cat_data in data['categories']:
            category, created = Category.objects.get_or_create(
                shop=shop,
                external_id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )
            category_map[cat_data['id']] = category
        
        # Импорт товаров
        for product_data in data['goods']:
            # Создание товара
            product, created = Product.objects.get_or_create(
                shop=shop,
                external_id=product_data['id'],
                defaults={
                    'category': category_map[product_data['category']],
                    'model': product_data['model'],
                    'name': product_data['name'],
                    'price': product_data['price'],
                    'price_rrc': product_data['price_rrc'],
                    'quantity': product_data['quantity']
                }
            )
            
            # Импорт параметров товара
            if 'parameters' in product_data:
                for param_name, param_value in product_data['parameters'].items():
                    ProductParameter.objects.create(
                        product=product,
                        name=param_name,
                        value=str(param_value)
                    )
        
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))