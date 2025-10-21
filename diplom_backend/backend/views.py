from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class RegisterBuyer(APIView):
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
        user = User.objects.create(
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            email=request.data['email'],
            company=request.data['company'],
            position=request.data['position']
        )
        user.set_password(request.data['password'])
        user.save()
        
        # Сериализация и возврат данных пользователя
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)