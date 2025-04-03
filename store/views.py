from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from store.models import Product

def home(request):
    products = Product.objects.all()
    # Создаём список продуктов с процентом скидки
    products_with_discount = []
    for product in products:
        discount_percent = None
        if product.discount_price and product.price > 0:
            discount_percent = round((1 - product.discount_price / product.price) * 100)
        products_with_discount.append({
            'product': product,
            'discount_percent': discount_percent
        })
    return render(request, 'home.html', {'products_with_discount': products_with_discount})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'home.html', {'login_form': form, 'open_login_modal': True})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'home.html', {'register_form': form, 'open_register_modal': True})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли!')
        return redirect('home')
    return redirect('home')