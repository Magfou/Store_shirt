# store/views.py
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile
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

    paginator = Paginator(products_with_discount, 10)
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
        return JsonResponse({'products': products_data})

    context = {
        'products_with_discount': products_with_discount,
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
                    price=cart_item.product.discount_price if cart_item.product.discount_price else cart_item.price
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
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        name = request.POST.get('name', '')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'home.html', {'open_register_modal': True})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'home.html', {'open_register_modal': True})

        user = User.objects.create_user(username=username, password=password1, first_name=name)
        user.save()
        login(request, user)
        messages.success(request, 'Вы успешно зарегистрировались!')
        return redirect('home')

    return render(request, 'home.html', {'open_register_modal': True})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('home')
    return redirect('home')

@login_required
def save_delivery_payment(request):
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        street = request.POST.get('street', '').strip()
        house = request.POST.get('house', '').strip()
        apartment = request.POST.get('apartment', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        card_expiry = request.POST.get('card_expiry', '').strip()
        card_cvv = request.POST.get('card_cvv', '').strip()

        # Проверка заполнения обязательных полей
        errors = {}
        if not city:
            errors['city'] = 'Поле "Город" обязательно для заполнения.'
        if not street:
            errors['street'] = 'Поле "Улица" обязательно для заполнения.'
        if not house:
            errors['house'] = 'Поле "Дом" обязательно для заполнения.'
        if not apartment:
            errors['apartment'] = 'Поле "Квартира" обязательно для заполнения.'
        if card_number and (not card_number.isdigit() or len(card_number) != 16):
            errors['card_number'] = 'Номер карты должен состоять из 16 цифр.'
        if card_expiry and not (len(card_expiry) == 5 and card_expiry[2] == '/' and card_expiry[:2].isdigit() and card_expiry[3:].isdigit()):
            errors['card_expiry'] = 'Срок действия должен быть в формате MM/YY.'
        if card_cvv and (not card_cvv.isdigit() or len(card_cvv) != 3):
            errors['card_cvv'] = 'CVV должен состоять из 3 цифр.'

        if errors:
            return render(request, 'base.html', {
                'open_delivery_payment_modal': True,
                'errors': errors,
                'form_data': {
                    'city': city,
                    'street': street,
                    'house': house,
                    'apartment': apartment,
                    'card_number': card_number,
                    'card_expiry': card_expiry,
                    'card_cvv': card_cvv,
                }
            })

        # Сохранение данных
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.city = city
        profile.street = street
        profile.house = house
        profile.apartment = apartment
        if card_number:
            profile.card_number = card_number
        if card_expiry:
            profile.card_expiry = card_expiry
        if card_cvv:
            profile.card_cvv = card_cvv
        profile.save()

        messages.success(request, 'Данные доставки и оплаты успешно сохранены!')
        return redirect('home')

    # При GET-запросе отображаем форму с текущими данными
    try:
        profile = UserProfile.objects.get(user=request.user)
        form_data = {
            'city': profile.city,
            'street': profile.street,
            'house': profile.house,
            'apartment': profile.apartment,
            'card_number': profile.card_number,
            'card_expiry': profile.card_expiry,
            'card_cvv': profile.card_cvv,
        }
    except UserProfile.DoesNotExist:
        form_data = {}

    return render(request, 'base.html', {
        'open_delivery_payment_modal': True,
        'form_data': form_data
    })

@login_required
def delete_card(request):
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.card_number = ''
            profile.card_expiry = ''
            profile.card_cvv = ''
            profile.save()
            messages.success(request, 'Данные карты успешно удалены!')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Профиль не найден.')
        return redirect('home')
    return redirect('home')