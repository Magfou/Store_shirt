from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'in_stock')
    list_filter = ('in_stock',)
    search_fields = ('name',)