#Модуль тестирования API. Исполняется отдельно от Django. Нужен requests

import requests
import json

# Настройки
BASE_URL = 'http://localhost:8000'
REGISTER_URL = f'{BASE_URL}/api/register/'

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

if __name__ == "__main__":
    print("=== Тест успешной регистрации ===")
    test_registration()
    
    print("\n=== Тест с отсутствующими полями ===")
    test_registration_missing_fields()
    
    print("\n=== Тест с дубликатом email ===")
    test_registration_duplicate_email()