from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from store.models import Product, Category
from django.core.paginator import Paginator
from django.http import JsonResponse

def home(request):
    # Получаем параметры из GET-запроса
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'price')  # По умолчанию сортировка по цене (возрастание)
    page_number = request.GET.get('page', 1)

    # Фильтрация товаров
    products = Product.objects.all()

    # Фильтр по поиску
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Фильтр по категории
    if category_id:
        try:
            products = products.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            pass

    # Фильтр по наличию (in_stock или -in_stock)
    if sort_by == 'in_stock':
        products = products.filter(in_stock=True)
        sort_by = 'price'  # После фильтрации сортируем по цене
    elif sort_by == '-in_stock':
        products = products.filter(in_stock=False)
        sort_by = 'price'  # После фильтрации сортируем по цене

    # Сортировка
    valid_sort_options = ['price', '-price']
    if sort_by in valid_sort_options:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('price')

    # Получаем все категории для выпадающего списка
    categories = Category.objects.all()

    # Обработка AJAX-запроса для динамической фильтрации
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products_data = []
        for product in products:
            discount_percent = None
            if product.discount_price and product.price > 0:
                discount_percent = round((1 - product.discount_price / product.price) * 100)
            products_data.append({
                'id': product.id,
                'name': product.name,
                'image': product.image.url if product.image else "https://via.placeholder.com/200",
                'price': float(product.price),
                'discount_price': float(product.discount_price) if product.discount_price else None,
                'discount_percent': discount_percent,
                'in_stock': product.in_stock,
            })
        return JsonResponse({'products': products_data})

    # Пагинация (10 товаров на страницу)
    paginator = Paginator(products, 10)
    products_page = paginator.get_page(page_number)

    # Создаём список продуктов с процентом скидки
    products_with_discount = []
    for product in products_page:
        discount_percent = None
        if product.discount_price and product.price > 0:
            discount_percent = round((1 - product.discount_price / product.price) * 100)
        products_with_discount.append({
            'product': product,
            'discount_percent': discount_percent
        })

    return render(request, 'home.html', {
        'products_with_discount': products_with_discount,
        'products_page': products_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'categories': categories,
        'selected_category': category_id,
    })

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