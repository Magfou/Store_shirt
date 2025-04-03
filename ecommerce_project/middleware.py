from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список путей, которые не требуют авторизации
        exempt_urls = [
            '/login/',
            '/register/',
            '/logout/',
            '/accounts/login/',
            '/accounts/logout/',
            '/',  # Главная страница не требует авторизации
        ]
        # Проверяем, является ли текущий путь одним из исключений
        if not request.user.is_authenticated and request.path not in exempt_urls:
            return redirect(reverse('login') + '?next=' + request.path)
        response = self.get_response(request)
        return response