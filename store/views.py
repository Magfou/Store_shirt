# store/views.py
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

def home(request):
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'price')

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if sort_by == 'in_stock':
        products = products.filter(in_stock=True)
    elif sort_by == '-in_stock':
        products = products.filter(in_stock=False)
    else:
        products = products.order_by(sort_by)

    products_with_discount = []
    for product in products:
        discount_percent = product.discount_percent
        products_with_discount.append({
            'product': product,
            'discount_percent': discount_percent
        })

    # Пагинация: 15 товаров на страницу (3 ряда по 5 карточек)
    paginator = Paginator(products_with_discount, 15)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    categories = Category.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = []
        for item in products_page:
            product = item['product']
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'discount_price': float(product.discount_price) if product.discount_price else None,
                'discount_percent': item['discount_percent'],
                'image': product.image.url if product.image else 'https://via.placeholder.com/200',
                'in_stock': product.in_stock,
            })

        # Формируем HTML для пагинации
        pagination_html = ''
        if products_page.has_other_pages():
            pagination_html += '<div class="pagination">'
            if products_page.has_previous():
                pagination_html += f'<a href="?page={products_page.previous_page_number}&search={search_query}&category={category_id}&sort={sort_by}" class="page-link">« Назад</a>'
            for num in products_page.paginator.page_range:
                if products_page.number == num:
                    pagination_html += f'<span class="page-link current">{num}</span>'
                else:
                    pagination_html += f'<a href="?page={num}&search={search_query}&category={category_id}&sort={sort_by}" class="page-link">{num}</a>'
            if products_page.has_next():
                pagination_html += f'<a href="?page={products_page.next_page_number}&search={search_query}&category={category_id}&sort={sort_by}" class="page-link">Вперёд »</a>'
            pagination_html += '</div>'

        return JsonResponse({
            'products': products_data,
            'pagination_html': pagination_html,
        })

    context = {
        'products_with_discount': products_page,  # Передаём объект пагинации
        'products_page': products_page,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    return render(request, 'home.html', context)

@login_required
def add_to_cart(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            
            total_items = sum(item.quantity for item in cart.items.all())
            
            cart_items = []
            for item in cart.items.all():
                cart_items.append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.discount_price if item.product.discount_price else item.product.price),
                    'total_price': float(item.total_price),
                    'image': item.product.image.url if item.product.image else 'https://via.placeholder.com/50',
                })
            
            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'cart_items': cart_items,
                'cart_total': float(cart.total_price),
            })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def get_cart(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = []
            for item in cart.items.all():
                cart_items.append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.discount_price if item.product.discount_price else item.product.price),
                    'total_price': float(item.total_price),
                    'image': item.product.image.url if item.product.image else 'https://via.placeholder.com/50',
                })
            return JsonResponse({
                'cart_items': cart_items,
                'cart_total': float(cart.total_price),
                'total_items': sum(item.quantity for item in cart.items.all()),
            })
        except Cart.DoesNotExist:
            return JsonResponse({
                'cart_items': [],
                'cart_total': 0.0,
                'total_items': 0,
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def remove_from_cart(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_item_id = request.POST.get('cart_item_id')
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            cart_item.delete()
            
            total_items = sum(item.quantity for item in cart.items.all())
            
            cart_items = []
            for item in cart.items.all():
                cart_items.append({
                    'id': item.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.product.discount_price if item.product.discount_price else item.product.price),
                    'total_price': float(item.total_price),
                    'image': item.product.image.url if item.product.image else 'https://via.placeholder.com/50',
                })
            
            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'cart_items': cart_items,
                'cart_total': float(cart.total_price),
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def checkout(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                messages.error(request, 'Корзина пуста.')
                return redirect('home')

            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price,
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.discount_price if cart_item.product.discount_price else cart_item.product.price
                )

            cart.items.all().delete()

            messages.success(request, f'Заказ #{order.id} успешно оформлен! Сумма: {order.total_price} $')
            return redirect('home')
        except Cart.DoesNotExist:
            messages.error(request, 'Корзина не найдена.')
            return redirect('home')
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
            return render(request, 'home.html', {'open_login_modal': True})
    return render(request, 'home.html', {'open_login_modal': True})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'home.html', {'open_register_modal': True})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'home.html', {'open_register_modal': True})

        try:
            user = User.objects.create_user(username=username, password=password1)
            if name:
                user.first_name = name
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'home.html', {'open_register_modal': True})
    return render(request, 'home.html', {'open_register_modal': True})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('home')
    return redirect('home')