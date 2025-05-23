from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = ['/login/', '/register/', '/logout/']

    def __call__(self, request):
        if not request.user.is_authenticated and not any(request.path.startswith(url) for url in self.exempt_urls):
            return redirect(reverse('login') + '?next=' + request.path)
        return self.get_response(request)