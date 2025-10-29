import yaml
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .serializers import UserSerializer, ProductSerializer, ProductInfoSerializer, ProductParameterSerializer, OrderItemSerializer, OrderSerializer, ContactSerializer
from .models import Shop, Parameter, Product, ProductInfo, Category, ProductParameter, Order, OrderItem, Contact

User = get_user_model()

class AccountRegister(APIView):
    def post(self, request):
        required_fields = ['first_name', 'last_name', 'email', 'password', 'company', 'position']
        
        # Проверка наличия всех обязательных полей
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {'error': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка, что пароль не пустой
        if not request.data['password']:
            return Response(
                {'error': 'Пароль не может быть пустым'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка уникальности email
        if User.objects.filter(email=request.data['email']).exists():
            return Response(
                {'error': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создание пользователя
        # Подтверждение по email убрано. Сразу активный
        user = User.objects.create(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            email=request.data['email'],
            company=request.data['company'],
            position=request.data['position'],
            is_active=True
        )
        user.set_password(request.data['password'])
        user.save()
        
        # Сериализация и возврат данных пользователя
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class AccountLogin(APIView):
    """
    Класс для авторизации пользователей
    """
    
    def post(self, request):
        # Проверяем обязательные поля
        if not {'email', 'password'}.issubset(request.data):
            return Response(
                {'Status': False, 'Errors': 'Не указаны email или пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Аутентификация пользователя
        user = authenticate(
            request, 
            username=request.data['email'], 
            password=request.data['password']
        )
        
        if user is not None:
            # Получаем или создаем токен
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'Status': True, 
                'Token': token.key
            })
        else:
            return Response({
                'Status': False, 
                'Errors': 'Неверный email или пароль'
            }, status=status.HTTP_401_UNAUTHORIZED)

class AccountDetails(APIView):
    """
    Класс для получения и редактирования данных пользователя
    """
    
    def get(self, request):
        """
        Получение данных текущего пользователя
        """
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Требуется авторизация'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(request.user)
        return Response({'Status': True, 'Data': serializer.data})
    
    def post(self, request):
        """
        Редактирование данных пользователя
        """
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Требуется авторизация'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Частичное обновление данных
        user_serializer = UserSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Status': True})
        else:
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class ImportShopYAML(APIView):
    """
    API для импорта данных из YAML файла
    """

    def import_data(self, data):

        stats = {
            'shop_created': False,
            'categories_processed': 0,
            'products_processed': 0,
            'parameters_processed': 0
        }
        
        # Создание или получение магазина
        shop, created = Shop.objects.get_or_create(name=data['shop'])
        stats['shop_created'] = created
        
        # Импорт категорий
        category_map = {}
        for cat_data in data['categories']:
            category, created = Category.objects.get_or_create(
                external_id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )
            category.shops.add(shop)
            category_map[cat_data['id']] = category
            stats['categories_processed'] += 1
        
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
            
            # Импорт параметров товара
            if 'parameters' in product_data:
                for param_name, param_value in product_data['parameters'].items():
                    parameter, _ = Parameter.objects.get_or_create(name=param_name)
                    
                    ProductParameter.objects.get_or_create(
                        product_info=product_info,
                        parameter=parameter,
                        defaults={'value': str(param_value)}
                    )
                    stats['parameters_processed'] += 1
            
            stats['products_processed'] += 1
        
        return stats
    
    def post(self, request):
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Требуется авторизация'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем наличие файла
        if 'file' not in request.FILES:
            return Response(
                {'Status': False, 'Error': 'YAML файл не предоставлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        yaml_file = request.FILES['file']
        
        try:
            # Чтение и парсинг YAML
            data = yaml.safe_load(yaml_file.read().decode('utf-8'))
            
            # Импорт данных
            result = self.import_data(data)
            
            return Response({
                'Status': True, 
                'Message': 'Данные успешно импортированы',
                'Details': result
            })
            
        except yaml.YAMLError as e:
            return Response(
                {'Status': False, 'Error': f'Ошибка парсинга YAML: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'Status': False, 'Error': f'Ошибка импорта: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ProductSearch(APIView):
    """
    Класс для поиска товаров по основным полям ProductInfo.
    """

    def get(self, request, *args, **kwargs):
 
        # Базовый запрос - только активные магазины
        query = Q(shop__state=True)
        
        # Параметры поиска
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        product_name = request.query_params.get('product_name')
        model_name = request.query_params.get('model')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        min_quantity = request.query_params.get('min_quantity')
        external_id = request.query_params.get('external_id')

        # Фильтр по магазину
        if shop_id:
            query = query & Q(shop_id=shop_id)

        # Фильтр по категории
        if category_id:
            query = query & Q(product__category_id=category_id)

        # Поиск по названию товара 
        if product_name:
            query = query & Q(product__name__icontains=product_name)

        # Поиск по модели товара
        if model_name:
            query = query & Q(model__icontains=model_name)

        # Фильтр по цене
        if min_price:
            query = query & Q(price__gte=min_price)
        if max_price:
            query = query & Q(price__lte=max_price)

        # Фильтр по количеству
        if min_quantity:
            query = query & Q(quantity__gte=min_quantity)

        # Фильтр по внешнему ID
        if external_id:
            query = query & Q(external_id=external_id)

        queryset = ProductInfo.objects.filter(
            query
        ).select_related(
            'shop', 
            'product', 
            'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)

class BasketView(APIView):
    """
    Класс для управления корзиной покупок пользователя.
    """

    def post(self, request, *args, **kwargs):
        """
        Добавить товары в корзину пользователя.
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)

        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = json.loads(items_string)
            except ValueError:
                return Response({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    
                    if serializer.is_valid():
                        try:
                            serializer.save()
                            objects_created += 1
                        except Exception as error:
                            return Response({'Status': False, 'Errors': str(error)})
                    else:
                        return Response({'Status': False, 'Errors': serializer.errors})

                return Response({'Status': True, 'Создано объектов': objects_created})
        
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
    
    def delete(self, request, *args, **kwargs):
        """
        Очистить корзину.
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)

        try:
            basket = Order.objects.get(user_id=request.user.id, state='basket')
            basket.delete()
            return Response({'Status': True, 'Удалено': 'Корзина очищена'})
        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Корзина не найдена'})
        except Exception as error:
            return Response({'Status': False, 'Error': str(error)})
    
    def get(self, request, *args, **kwargs):
        """
        Получить текущую корзину пользователя.
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)

        try:
            basket = Order.objects.get(user_id=request.user.id, state='basket')
            serializer = OrderSerializer(basket)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Корзина не найдена'})
        except Exception as error:
            return Response({'Status': False, 'Error': str(error)})
        
class ContactView(APIView):
    """
    Класс для управления контактами пользователя
    """
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        request.data['user'] = request.user.id
            
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response({'Status': True, 'id': contact.id})
        return Response({'Status': False, 'Errors': serializer.errors})
    
    def put(self, request, contact_id):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)

        try:
            contact = Contact.objects.get(id=contact_id, user_id=request.user.id)
        except Contact.DoesNotExist:
            return Response({'Status': False, 'Error': 'Contact not found'})
        
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'Status': True})
        return Response({'Status': False, 'Errors': serializer.errors})
    
    def delete(self, request, contact_id):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)

        try:
            contact = Contact.objects.get(id=contact_id, user_id=request.user.id)
            contact.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({'Status': False, 'Error': 'Contact not found'})

class OrderView(APIView):
    """
    Класс для получения и размещения заказов пользователями
    """

    def get(self, request, order_id=None):
        """
        Получение заказов пользователя
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user_id=request.user.id)
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            except Order.DoesNotExist:
                return Response({'Status': False, 'Error': 'Заказ не найден'})
        else:
            orders = Order.objects.filter(user_id=request.user.id).exclude(state='basket')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Создание нового заказа из корзины
        Аргументы:
        - contact_id: ID контакта для доставки
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'Status': False, 'Error': 'Не указан контакт'})
        
        try:
            basket = Order.objects.get(user_id=request.user.id, state='basket')
            contact = Contact.objects.get(id=contact_id, user_id=request.user.id)
        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Корзина не найдена'})
        except Contact.DoesNotExist:
            return Response({'Status': False, 'Error': 'Контакт не найден'})
        
        if not basket.ordered_items.exists():
            return Response({'Status': False, 'Error': 'Корзина пуста'})
        
        basket.contact = contact
        basket.state = 'new'
        basket.save()
        
        # Отправка подтверждения заказа клиенту
        self.send_confirmation_email(basket)
        
        return Response({'Status': True, 'order_id': basket.id})

    def put(self, request, order_id):
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        try:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
            
            # Обновляем контакт если передан
            contact_id = request.data.get('contact_id')
            if contact_id:
                contact = Contact.objects.get(id=contact_id, user_id=request.user.id)
                order.contact = contact
            
            # Отправляем накладную при изменении статуса на "собран" или "отправлен"
            new_state = request.data.get('state')
            print(new_state, order.state)
            if new_state in ['assembled', 'sent']:
                order.state = new_state
                order.save()
                
                # Автоматическая отправка накладной
                self.send_invoice_email(order)
            elif new_state == 'confirmed':
                # Отправка подтверждения при подтверждении заказа
                order.state = new_state
                order.save()
                self.send_confirmation_email(order)
            else:
                order.save()
                
            return Response({'Status': True,'State':order.state})
            
        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Заказ не найден'})
        except Contact.DoesNotExist:
            return Response({'Status': False, 'Error': 'Контакт не найден'})

    def delete(self, request, order_id):
        """
        Удаление заказа
        """
        if not request.user.is_authenticated:
            return Response({'Status': False, 'Error': 'Log in required'}, status=403)
        
        try:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
            order.delete()
            return Response({'Status': True}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({'Status': False, 'Error': 'Заказ не найден'})
    
    def send_invoice_email(self, order):
        print(f"Send email for order id={order.id}")
        
        try:
            # Email администратора (можно вынести в settings)
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
            
            # Тема письма
            subject = f'Накладная для заказа #{order.id} от {order.dt.strftime("%d.%m.%Y")}'
            
            # Данные для шаблона
            context = {
                'order': order,
                'order_items': order.ordered_items.all().select_related(
                    'product_info', 
                    'product_info__product',
                    'product_info__shop'
                ),
                'total_sum': order.total_sum,
                'contact': order.contact,
            }
            
            
            message = render_to_string('emails/order_invoice.txt', context)
            html_message = render_to_string('emails/order_invoice.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email: {str(e)}")
            return False
        
    def send_confirmation_email(self, order):
        """
        Отправка подтверждения заказа на email клиента
        """
        print(f"Send confirmation email for order id={order.id}")
        
        try:
            # Email клиента
            client_email = order.user.email
            
            # Тема письма
            subject = f'Подтверждение заказа #{order.id} от {order.dt.strftime("%d.%m.%Y")}'
            
            # Данные для шаблона
            context = {
                'order': order,
                'order_items': order.ordered_items.all().select_related(
                    'product_info', 
                    'product_info__product',
                    'product_info__shop'
                ),
                'total_sum': order.total_sum,
                'contact': order.contact,
                'user': order.user,
            }
            
            # Рендерим текстовую и HTML версии письма
            message = render_to_string('emails/order_confirmation.txt', context)
            html_message = render_to_string('emails/order_confirmation.html', context)
            
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"Confirmation email sent to {client_email}")
            return True
            
        except Exception as e:
            print(f"Ошибка отправки email подтверждения: {str(e)}")
            return False