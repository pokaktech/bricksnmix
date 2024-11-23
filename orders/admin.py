from django.contrib import admin
from .models import *




admin.site.register(CustomerOrder)
admin.site.register(OrderItem)
admin.site.register(OrderProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
