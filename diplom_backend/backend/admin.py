from django.contrib import admin
from .models import Shop,Category,Product,ProductInfo,Parameter,ProductParameter,Contact,Order,OrderItem,ConfirmEmailToken


admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductInfo)
admin.site.register(Parameter)
admin.site.register(ProductParameter)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ConfirmEmailToken)