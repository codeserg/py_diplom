from django.urls import path

from .views import BuyerRegister,BuyerLogin

app_name = 'backend'
urlpatterns = [
    path('user/register', BuyerRegister.as_view(), name='buyer-register'),
    path('user/login', BuyerLogin.as_view(), name='buyer-login'),
]