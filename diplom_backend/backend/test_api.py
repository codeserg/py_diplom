#Модуль тестирования API. Исполняется отдельно от Django. Нужен requests
import os 
import requests
import json

# Настройки
BASE_URL = 'http://localhost:8000'
REGISTER_URL = f'{BASE_URL}/api/v1/user/register'
LOGIN_URL = f'{BASE_URL}/api/v1/user/login'    
DETAILS_URL = f'{BASE_URL}/api/v1/user/details'
IMPORT_URL = f'{BASE_URL}/api/v1/import'

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


if __name__ == "__main__":
    """
    print("=== Тест успешной регистрации ===")
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

    """
    
    import_test()