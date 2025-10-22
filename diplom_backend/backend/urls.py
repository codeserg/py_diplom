from django.urls import path

from .views import AccountRegister, AccountLogin, AccountDetails,ImportShopYAML,ProductSearch,BasketView

app_name = 'backend'
urlpatterns = [
    path('user/register', AccountRegister.as_view(), name='account-register'),
    path('user/login', AccountLogin.as_view(), name='account-login'),
    path('user/details', AccountDetails.as_view(), name='account-details'),
    path('import', ImportShopYAML.as_view(), name='import-shop'),
    path('productsearch', ProductSearch.as_view(), name='product-search'),
    path('basket', BasketView.as_view(), name='basket'),

]