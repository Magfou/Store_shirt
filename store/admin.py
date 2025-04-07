# store/admin.py
from django.contrib import admin
from .models import Category, Product, ProductSpecification, Cart, CartItem, Order, OrderItem, Payment, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'in_stock', 'category', 'average_rating')
    list_filter = ('in_stock', 'category')
    search_fields = ('name',)

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value')
    list_filter = ('product',)
    search_fields = ('name', 'value')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    search_fields = ('product__name',)

# store/admin.py
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    list_editable = ('status',)  # Позволяет редактировать статус прямо в списке

    # Определяем действия для изменения статуса
    actions = ['set_status_pending', 'set_status_processing', 'set_status_shipped', 'set_status_delivered', 'set_status_cancelled']

    def set_status_pending(self, request, queryset):
        queryset.update(status='PENDING')
        self.message_user(request, "Статус выбранных заказов изменён на 'PENDING'.")
    set_status_pending.short_description = "Изменить статус на PENDING"

    def set_status_processing(self, request, queryset):
        queryset.update(status='PROCESSING')
        self.message_user(request, "Статус выбранных заказов изменён на 'PROCESSING'.")
    set_status_processing.short_description = "Изменить статус на PROCESSING"

    def set_status_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
        self.message_user(request, "Статус выбранных заказов изменён на 'SHIPPED'.")
    set_status_shipped.short_description = "Изменить статус на SHIPPED"

    def set_status_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
        self.message_user(request, "Статус выбранных заказов изменён на 'DELIVERED'.")
    set_status_delivered.short_description = "Изменить статус на DELIVERED"

    def set_status_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, "Статус выбранных заказов изменён на 'CANCELLED'.")
    set_status_cancelled.short_description = "Изменить статус на CANCELLED"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('product__name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'created_at')
    list_filter = ('method', 'status')
    search_fields = ('order__id',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')