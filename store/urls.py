from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('get-cart/', views.get_cart, name='get_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
]