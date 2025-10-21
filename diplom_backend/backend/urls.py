from django.urls import path

from .views import RegisterBuyer

app_name = 'backend'
urlpatterns = [
    path('user/register', RegisterBuyer.as_view(), name='buyer-register'),
]