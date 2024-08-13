from django.contrib import admin

from .models import Product, Topping, Cart, CartItem, Order, OrderItem

# Register your models here.
admin.site.register(Product)
admin.site.register(Topping)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)