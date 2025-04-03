from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django import forms
from .models import Product

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=False, label="Name")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('name',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
        if commit:
            user.save()
        return user

def home(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    # Тестовые данные товаров с учётом скидок
    products = [
        Product(name="Футболка", price=19.99, discount_price=14.99, in_stock=True),
        Product(name="Джинсы", price=49.99, discount_price=None, in_stock=False),
        Product(name="Кроссовки", price=79.99, discount_price=59.99, in_stock=True),
        Product(name="Куртка", price=99.99, discount_price=None, in_stock=True),
        Product(name="Шапка", price=14.99, discount_price=9.99, in_stock=False),
        Product(name="Рюкзак", price=39.99, discount_price=None, in_stock=True),
    ]
    return render(request, 'home.html', {
        'login_form': login_form,
        'register_form': register_form,
        'open_login_modal': request.GET.get('next') is not None,
        'products': products
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Регистрация успешна! Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте введённые данные.')
            return render(request, 'home.html', {
                'login_form': AuthenticationForm(),
                'register_form': form,
                'open_register_modal': True
            })
    return redirect('home')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вход успешен! Привет, {user.username}!')
            next_url = request.POST.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Ошибка входа. Неверное имя пользователя или пароль.')
            return render(request, 'home.html', {
                'login_form': form,
                'register_form': CustomUserCreationForm(),
                'open_login_modal': True
            })
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    return render(request, 'home.html', {
        'login_form': login_form,
        'register_form': register_form,
        'open_login_modal': True
    })