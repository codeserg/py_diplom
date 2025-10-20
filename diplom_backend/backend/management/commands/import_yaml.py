import yaml
from django.core.management.base import BaseCommand
from backend.models import Shop, Category, Product, ProductInfo, ProductParameter

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
            # Создаем или получаем категорию (без привязки к магазину)
            category, created = Category.objects.get_or_create(
                external_id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )
            # Добавляем магазин к категории через связь ManyToMany
            category.shops.add(shop)
            category_map[cat_data['id']] = category
        
        # Импорт товаров
        for product_data in data['goods']:
            # Создание товара
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                shop=shop,
                category=category_map[product_data['category']],
                defaults={}
            )
            
            # Создание информации о продукте
            product_info, created = ProductInfo.objects.get_or_create(
                external_id=product_data['id'],
                product=product,
                shop=shop,
                defaults={
                    'model': product_data.get('model', ''),
                    'quantity': product_data['quantity'],
                    'price': product_data['price'],
                    'price_rrc': product_data['price_rrc']
                }
            )
            """
            # Импорт параметров товара
            if 'parameters' in product_data:
                for param_name, param_value in product_data['parameters'].items():
                    # Создаем или получаем параметр
                    parameter, _ = Parameter.objects.get_or_create(name=param_name)
                    
                    # Создаем связь параметра с продуктом
                    ProductParameter.objects.get_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': str(param_value)}
                    )
                """