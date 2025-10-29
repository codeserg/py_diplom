# 🛍️ Дипломный проект Backend API магазина

Backend-система для интернет-магазина с REST API, реализованная на Django и Django REST Framework.

##  Установка и запуск

### Предварительные требования
- Python 3.8+
- pip (менеджер пакетов Python)

### Шаги установки

1. **Клонирование проекта**
   ```bash
   git clone <url-репозитория>
   cd <папка-проекта>
   ```

2. **Установка зависимостей**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройка базы данных**
   ```bash
   # Если нужно удалить существующую базу данных
   python manage.py migrate
   ```

4. **Запуск сервера**
   ```bash
   python manage.py runserver
   ```

## Тестирование

Для проверки работоспособности API доступны тесты:
```bash
python manage.py test diplom_backend\backend\test_api.py
```

## Импорт данных

Система поддерживает импорт данных магазина через два способа:

### Через Django команды
```bash
# Импорт тестовых данных
python manage.py import_yaml sample_shop.yaml
python manage.py import_yaml test_shop.yaml
```

### Через API
- **POST** `/api/v1/import/` - импорт данных магазина из YAML

## API методы

### 👤 Аутентификация и профиль
- **POST** `/api/v1/account/register/` - регистрация пользователя
- **POST** `/api/v1/account/login/` - авторизация пользователя  
- **GET** `/api/v1/account/details/` - получение данных пользователя
- **POST** `/api/v1/account/details/` - редактирование данных пользователя

### Поиск товаров
- **GET** `/api/v1/productsearch/` - поиск товаров

### Корзина покупок
- **POST** `/api/v1/basket/` - добавление товаров в корзину
- **GET** `/api/v1/basket/` - получение содержимого корзины
- **DELETE** `/api/v1/basket/` - очистка корзины

### Контакты
- **GET** `/api/v1/contact/` - получение списка контактов
- **POST** `/api/v1/contact/` - добавление нового контакта
- **PUT** `/api/v1/contact/{id}/` - редактирование контакта
- **DELETE** `/api/v1/contact/{id}/` - удаление контакта

### Управление заказами
- **GET** `/api/v1/order/` - список всех заказов
- **POST** `/api/v1/order/` - создание заказа из корзины
- **GET** `/api/v1/order/{id}/` - получение информации о заказе
- **PUT** `/api/v1/order/{id}/` - обновление заказа
- **DELETE** `/api/v1/order/{id}/` - удаление заказа

## Уведомления по email

Система автоматически отправляет email-уведомления:

### Администратору при:
- Смене статуса заказа на **"Собран"**
- Смене статуса заказа на **"Отправлен"**

### Клиенту при:
- Отправке корзины (создании заказа)

### Настройка email

По умолчанию используется консольный бэкенд для тестирования:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Для реальной отправки email добавьте в `settings.py`:

```python
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@yandex.ru'
EMAIL_HOST_PASSWORD = 'your_app_password'
```
---

