#Модуль тестирования API. Исполняется отдельно от Django. Нужен requests
import os 
import requests
import json

# Настройки
BASE_URL = 'http://localhost:8000'
REGISTER_URL = f'{BASE_URL}/api/v1/user/register/'
LOGIN_URL = f'{BASE_URL}/api/v1/user/login/'    
DETAILS_URL = f'{BASE_URL}/api/v1/user/details/'
IMPORT_URL = f'{BASE_URL}/api/v1/import/'
PRODUCT_SEARCH_URL = f'{BASE_URL}/api/v1/productsearch/'
BASKET_URL = f'{BASE_URL}/api/v1/basket/'
CONTACT_URL =f'{BASE_URL}/api/v1/contact/'
ORDER_URL =f'{BASE_URL}/api/v1/order/'

def test_registration():
    """Тест успешной регистрации"""
    data = {
        'first_name': 'Иван',
        'last_name': 'Петров',
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123',
        'company': 'ООО Ромашка',
        'position': 'Менеджер'
    }
    
    try:
        response = requests.post(REGISTER_URL, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения. Убедитесь, что сервер запущен.")
        return None

def test_registration_missing_fields():
    """Тест регистрации с отсутствующими полями"""
    data = {
        'first_name': 'Иван',
        'email': 'test@example.com',
        # отсутствуют last_name, password, company, position
    }
    
    response = requests.post(REGISTER_URL, json=data)
    print(f"\nMissing fields test - Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response

def test_registration_duplicate_email():
    """Тест регистрации с существующим email"""
    data = {
        'first_name': 'Петр',
        'last_name': 'Иванов',
        'email': 'ivan.petrov@example.com',  # тот же email
        'password': 'anotherpassword',
        'company': 'ООО Лютик',
        'position': 'Директор'
    }
    
    response = requests.post(REGISTER_URL, json=data)
    print(f"\nDuplicate email test - Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response

def test_user_login():
    
    login_credentials = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_credentials)
    print(f"Статус логина: {login_response.status_code}")
    print(f"Ответ логина: {login_response.json()}")
    
    # Проверяем успешность логина
    if login_response.status_code == 200:
        response_data = login_response.json()
        if response_data.get('Status') and 'Token' in response_data:
            print("Логин успешен! Токен получен.")
            print(f"Токен: {response_data['Token']}...")
            return True
        else:
            print("Логин неудачен: токен не получен")
            return False
    else:
        print("Ошибка при логине")
        return False

def test_login_with_wrong_password():
    """Тест логина с неправильным паролем"""
    
    
    wrong_credentials = {
        'email': 'ivan.petrov@example.com',
        'password': 'wrongpassword'
    }
    
    response = requests.post(LOGIN_URL, json=wrong_credentials)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 401 or (response.json().get('Status') == False):
        print("Тест пройден: система отклонила неверные учетные данные")
        return True
    else:
        print("Тест не пройден: система приняла неверные учетные данные")
        return False

def test_account_details():
    
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    
   
    headers = {'Authorization': f'Token {token}'}
    
    # 2. Тест получения данных (GET)
    print("\n=== Получение данных пользователя ===")
    get_response = requests.get(DETAILS_URL, headers=headers)
    print(f"Status: {get_response.status_code}")
    print(f"Data: {get_response.json()}")
    
    # 3. Тест изменения данных (POST)
    print("\n=== Изменение данных пользователя ===")
    update_data = {
        'first_name': 'Григорий',
        'last_name': 'Волков',
        'company': 'ООО Прогресс'
    }
    
    post_response = requests.post(DETAILS_URL, json=update_data, headers=headers)
    print(f"Status: {post_response.status_code}")
    print(f"Response: {post_response.json()}")
    
    print("\n=== Проверка изменений ===")
    get_response_after = requests.get(DETAILS_URL, headers=headers)
    print (get_response_after.json())

def import_test():
    
    login = requests.post(LOGIN_URL , json={
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    })
    token = login.json()['Token']
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', 'test_shop.yaml')
    with open(file_path, 'rb') as file:  
        response = requests.post(IMPORT_URL ,
            files={'file': file},
            headers={'Authorization': f'Token {token}'}
        )
    
    print("Status:", response.status_code)
    print("Response:", response.json())


def test_product_search():

    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }

    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    

    headers = {'Authorization': f'Token {token}'}
    
    print("\n\nПоиск по названию товара:\n")
    params = {'product_name': 'iPhone'}
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    print(f"\nСтатус: {response.status_code}")
    print(f"\n{response.json()}\n")

    print("\n\nПоиск по модели:\n")
    params = {'model': 'Pro'}
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    print(f"\nСтатус: {response.status_code}")
    print(f"\n{response.json()}\n")
    
    
    print("\n\nПоиск по диапазону цен\n")
    params = {'min_price': 50000, 'max_price': 100000}
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    print(f"\nСтатус: {response.status_code}")
    print(f"\n{response.json()}\n")
       
  
    print("\n\nКомбинированный поиск\n")
    params = {
        'product_name': 'Samsung',
        'min_price': 20000,
        'min_quantity': 5
    }
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    print(f"\nСтатус: {response.status_code}")
    print(f"\n{response.json()}\n")
    
    

    print("\n\nПоиск по магазину и категории\n")
    params = {
        'shop_id': 1,
        'category_id': 3
    }
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    print(f"\nСтатус: {response.status_code}")
    print(f"\n{response.json()}\n")
    

def test_basket_post_without_auth():
    """Тест добавления в корзину без авторизации"""
    
    # Данные для добавления в корзину
    items_data = [
        {
            "product_info": 123,
            "quantity": 2
        }
    ]
    
    response = requests.post(BASKET_URL, json={'items': json.dumps(items_data)})
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 403 or (response.json().get('Status') == False and 'Log in required' in str(response.json())):
        print("Тест пройден: система требует авторизацию")
        return True
    else:
        print("Тест не пройден: система разрешила доступ без авторизации")
        return False
    
def test_basket_post():
    """Тест добавления в корзину"""
    
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    headers = {'Authorization': f'Token {token}'}
    
    #сначала ищем id товара
    params = {'product_name': 'iPhone'}
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    id = response.json()[0].get("id")
    print (f"\nНайден товар id {id}")
    items_data = [
        {
            "product_info": id,
            "quantity": 3
        }
    ]
    print("\n Очистка корзины. Тест метода delete\n")
    response = requests.delete(BASKET_URL, headers=headers)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")

    response = requests.post(BASKET_URL, json={'items': json.dumps(items_data)}, headers=headers)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200 and response.json().get('Status') == True and response.json().get('Создано объектов', 0) > 0:
        print("Тест пройден: товар успешно добавлен в корзину")
        return True
    else:
        print("Тест не пройден: не удалось добавить товар в корзину")
        return False

def test_basket_get():
    print("\n","-"*32,"Тест получения корзины","-"*32)
    
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    headers = {'Authorization': f'Token {token}'}

    response = requests.get(BASKET_URL, headers=headers)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
    if response.status_code == 200 and 'id' in response.json():
        print("Тест пройден: корзина успешно получена")
        return True
    else:
        print("Тест не пройден: не удалось получить корзину")
        return False
    
def test_contact_crud():
    print("\n","-"*32,"Тестирование методов работы с контактом","-"*32)
    
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    headers = {'Authorization': f'Token {token}'}

    # POST
    contact_data = {
        'city': 'Москва',
        'street': 'Ленина',
        'house': '10',
        'phone': '+79991234567'
    }
    response = requests.post(CONTACT_URL, json=contact_data, headers=headers)
    print(f"POST Статус: {response.status_code}")
    print(f"POST Ответ: {response.json()}\n")
    contact_id = response.json().get('id')

    # GET всех контактов
    response = requests.get(CONTACT_URL, headers=headers)
    print(f"GET Статус: {response.status_code}")
    print(f"GET Ответ: {response.json()}\n")

    # PUT
    update_data = {'city': 'Санкт-Петербург'}
    response = requests.put(f"{CONTACT_URL}{contact_id}/", json=update_data, headers=headers)
    print(f"PUT Статус: {response.status_code}")
    print(f"PUT Ответ: {response.json()}\n")

    # DELETE
    response = requests.delete(f"{CONTACT_URL}{contact_id}/", headers=headers)
    print(f"DELETE Статус: {response.status_code}")

def test_order_post():
    print("\n","-"*32,"Тест создания заказа из корзины","-"*32)
        
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    headers = {'Authorization': f'Token {token}'}

    # ОЧИСТКА КОРЗИНЫ перед тестом
    response = requests.delete(BASKET_URL, headers=headers)
    
    # Создаем контакт
    contact_data = {
        'city': 'Москва',
        'street': 'Ленина',
        'house': '10',
        'phone': '+79991234567'
    }
    response = requests.post(CONTACT_URL, json=contact_data, headers=headers)
    contact_id = response.json().get('id')
    print(f"Создан контакт id {contact_id}")

    # Добавляем товар в корзину
    params = {'product_name': 'iPhone'}
    response = requests.get(PRODUCT_SEARCH_URL, headers=headers, params=params)
    product_id = response.json()[0].get("id")
    print(f"Найден товар id {product_id}")
    
    items_data = [{"product_info": product_id, "quantity": 1}]
    response = requests.post(BASKET_URL, json={'items': json.dumps(items_data)}, headers=headers)
    print(f"Добавлено в корзину: {response.json()}")

    # Создаем заказ
    order_data = {'contact_id': contact_id}
    response = requests.post(ORDER_URL, json=order_data, headers=headers)
    print(f"POST Order Status: {response.status_code}")
    print(f"POST Order Response: {response.json()}")

    if response.status_code == 200 and response.json().get('Status') == True:
        print("Тест пройден: заказ успешно создан")
        return True
    else:
        print("Тест не пройден: не удалось создать заказ")
        return False
    
def test_order_put():
    print("\n","-"*32,"Тест обновления заказа","-"*32)
        
    login_data = {
        'email': 'ivan.petrov@example.com',
        'password': 'securepassword123'
    }
    
    login_response = requests.post(LOGIN_URL, json=login_data)
    token = login_response.json().get('Token')
    headers = {'Authorization': f'Token {token}'}

    # Создаем второй контакт для обновления
    contact_data = {
        'city': 'Санкт-Петербург',
        'street': 'Невский',
        'house': '25',
        'phone': '+79997654321'
    }
    response = requests.post(CONTACT_URL, json=contact_data, headers=headers)
    new_contact_id = response.json().get('id')
    print(f"Создан новый контакт id {new_contact_id}")

    # Получаем ID существующего заказа
    response = requests.get(ORDER_URL, headers=headers)
    orders = response.json()
    if orders:
        order_id = orders[0].get('id')
        print(f"Найден заказ id {order_id}")

        # Обновляем заказ
        update_data = {'contact_id': new_contact_id}
        response = requests.put(f"{ORDER_URL}{order_id}/", json=update_data, headers=headers)
        print(f"PUT Order Status: {response.status_code}")
        print(f"PUT Order Response: {response.json()}")

        if response.status_code == 200 and response.json().get('Status') == True:
            print("Тест пройден: заказ успешно обновлен")
            return True
        else:
            print("Тест не пройден: не удалось обновить заказ")
            return False
    else:
        print("Нет заказов для тестирования")
        return False

if __name__ == "__main__":
    """
    print("=== Тест регистрации ===")
    test_registration()
    
    print("\n=== Тест с отсутствующими полями ===")
    test_registration_missing_fields()
    
    print("\n=== Тест с дубликатом email ===")
    test_registration_duplicate_email()

    print("\n=== Тест логина ===")
    test_user_login()
  
    print("\n=== Тест с неправильным паролем ===")
    test_login_with_wrong_password()

    test_account_details()
   
    import_test()
    
    test_product_search()
    
    test_basket_post_without_auth()
    
    test_basket_post()

    test_basket_get()
    
    test_contact_crud()
    
    test_order_post()
    """
    test_order_put()