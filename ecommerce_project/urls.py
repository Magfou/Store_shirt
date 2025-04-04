from django.contrib import admin
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Админка
    path('', views.home, name='home'),  # Главная страница
    path('login/', views.login_view, name='login'),  # Вход
    path('register/', views.register_view, name='register'),  # Регистрация
    path('logout/', views.logout_view, name='logout'),  # Выход
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)