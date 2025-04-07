# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('get_cart/', views.get_cart, name='get_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('delivery_payment/', views.delivery_payment, name='delivery_payment'),  # Новый URL
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]