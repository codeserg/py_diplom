Импорта товаров реализован через API и как команда Django

manage.py import_yaml sample_shop.yaml
manage.py import_yaml test_shop.yaml


Реализованы методы: 

**Методы регистрации и авторизации:**
POST /api/v1/account/register/ - регистрация пользователя
POST /api/v1/account/login/ - авторизация пользователя
GET /api/v1/account/details/ - получение данных пользователя
POST /api/v1/account/details/ - редактирование данных пользователя

**Методы импорта данных:**
POST /api/v1/import/ - импорт данных магазина из YAML

**Методы поиска товаров:**
GET /api/v1/productsearch/ - поиск товаров

**Методы корзины:**
POST /api/v1/basket/ - добавление товаров в корзину
GET /api/v1/basket/ - получение корзины
DELETE /api/v1/basket/ - очистка корзины

**Методы контактов:**
GET /api/v1/contact/ - получение списка контактов
POST /api/v1/contact/ - добавление контакта
PUT /api/v1/contact/1/ - редактирование контакта с ID=1
DELETE /api/v1/contact/1/ - удаление контакта с ID=1

**Методы заказа:**
GET /api/v1/order/ - список всех заказов
POST /api/v1/order/ - создание заказа из корзины
GET /api/v1/order/1/ - получение заказа с ID=1
PUT /api/v1/order/1/ - обновление заказа с ID=1
DELETE /api/v1/order/1/ - удаление заказа с ID=1