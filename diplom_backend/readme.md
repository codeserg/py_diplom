Импорта товаров реализован через API и как команда Django

manage.py import_yaml sample_shop.yaml
manage.py import_yaml test_shop.yaml


Методы заказа: 
GET /api/v1/order/ - список всех заказов
POST /api/v1/order/ - создание заказа из корзины
GET /api/v1/order/1/ - получение заказа с ID=1
PUT /api/v1/order/1/ - обновление заказа с ID=1
DELETE /api/v1/order/1/ - удаление заказа с ID=1