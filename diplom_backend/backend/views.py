from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer

User = get_user_model()

class BuyerRegister(APIView):
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
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



class BuyerLogin(APIView):
    """
    Класс для авторизации покупателей
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