# store/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import stripe
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment, Review

# Настройка Stripe (замените на ваш секретный ключ)
stripe.api_key = 'sk_test_51RApJYPNAUNwoBnEAfZkaQrZemAYYvIoMl8i0NMgNxgxXbhwGlBv5vtH1reIbF5tfXQo4zDYgxkBzO9Us8BVuOVc00lmuviAtl'

@login_required
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Фильтры
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', 'price')

    if search_query:
        products = products.filter(Q(name__icontains=search_query))
    if category_id:
        products = products.filter(category_id=category_id)

    if sort_by:
        products = products.order_by(sort_by)

    # Пагинация для продуктов
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page', 1)
    products_page = paginator.get_page(page_number)

    # Вычисляем скидки для текущей страницы
    products_with_discount = []
    for product in products_page:
        discount_percent = None
        if product.discount_price:
            discount_percent = int(((product.price - product.discount_price) / product.price) * 100)
        products_with_discount.append({
            'product': product,
            'discount_percent': discount_percent
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = []
        for item in products_with_discount:
            product = item['product']
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'discount_price': float(product.discount_price) if product.discount_price else None,
                'discount_percent': item['discount_percent'],
                'image': product.image.url if product.image else 'https://via.placeholder.com/200',
                'in_stock': product.in_stock,
                'average_rating': product.average_rating,
                'review_count': product.reviews.count(),
            })

        pagination_html = render_to_string('pagination.html', {
            'products_page': products_page,
            'search_query': search_query,
            'selected_category': category_id,
            'sort_by': sort_by,
        }, request=request)

        return JsonResponse({
            'products': products_data,
            'pagination_html': pagination_html,
        })

    context = {
        'products_with_discount': products_with_discount,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'sort_by': sort_by,
        'products_page': products_page,
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
        cart, created = Cart.objects.get_or_create(user=request.user)
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

            payment_method = request.POST.get('payment_method')
            if not payment_method:
                messages.error(request, 'Выберите способ оплаты.')
                return redirect('checkout')

            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price,
                status='PENDING'
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.discount_price if cart_item.product.discount_price else cart_item.product.price
                )

            Payment.objects.create(
                order=order,
                amount=order.total_price,
                method=payment_method,
                status='PENDING' if payment_method != 'CASH_ON_DELIVERY' else 'COMPLETED'
            )

            if payment_method in ['CARD', 'PAYPAL']:
                return redirect('process_payment', order_id=order.id)

            cart.delete()
            messages.success(request, f'Заказ #{order.id} успешно оформлен! Сумма: {order.total_price} $')
            return redirect('home')
        except Cart.DoesNotExist:
            messages.error(request, 'Корзина не найдена.')
            return redirect('home')

    return render(request, 'checkout.html', {})

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payments.first()

    if payment.status == 'COMPLETED':
        messages.success(request, f'Заказ #{order.id} уже оплачен!')
        return redirect('home')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Заказ #{order.id}',
                    },
                    'unit_amount': int(order.total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment_success/') + f'?order_id={order.id}',
            cancel_url=request.build_absolute_uri('/payment_cancel/') + f'?order_id={order.id}',
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Ошибка при обработке платежа: {str(e)}')
        return redirect('checkout')

@login_required
def payment_success(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payments.first()
    payment.status = 'COMPLETED'
    payment.save()
    order.status = 'PENDING'
    order.save()
    cart = Cart.objects.get(user=request.user)
    cart.delete()
    messages.success(request, f'Оплата заказа #{order.id} успешно завершена!')
    return redirect('home')

@login_required
def payment_cancel(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.error(request, f'Оплата заказа #{order.id} была отменена.')
    return redirect('checkout')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

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
        email = request.POST.get('email')
        name = request.POST.get('name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'home.html', {'open_register_modal': True})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'home.html', {'open_register_modal': True})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Этот email уже используется.')
            return render(request, 'home.html', {'open_register_modal': True})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
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

# Функция для проверки, купил ли пользователь товар
def has_purchased_product(user, product):
    return Order.objects.filter(
        user=user,
        items__product=product,
        status__in=['SHIPPED', 'DELIVERED']
    ).exists()

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    specifications = product.specifications.all()

    # Проверяем, купил ли пользователь товар
    can_review = has_purchased_product(request.user, product)

    # Проверяем, оставил ли пользователь уже отзыв
    has_reviewed = Review.objects.filter(product=product, user=request.user).exists()

    if request.method == 'POST' and can_review and not has_reviewed:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            messages.error(request, 'Пожалуйста, укажите оценку и комментарий.')
        else:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    Review.objects.create(
                        product=product,
                        user=request.user,
                        rating=rating,
                        comment=comment
                    )
                    product.update_average_rating()
                    messages.success(request, 'Ваш отзыв успешно добавлен!')
                else:
                    messages.error(request, 'Оценка должна быть от 1 до 5.')
            except ValueError:
                messages.error(request, 'Неверный формат оценки.')
        return redirect('product_detail', product_id=product.id)

    context = {
        'product': product,
        'reviews': reviews,
        'specifications': specifications,
        'can_review': can_review and not has_reviewed,
        'average_rating': product.average_rating,
        'review_count': reviews.count(),
    }
    return render(request, 'product_detail.html', context)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            messages.error(request, 'Пожалуйста, укажите оценку и комментарий.')
        else:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    review.rating = rating
                    review.comment = comment
                    review.save()
                    review.product.update_average_rating()
                    messages.success(request, 'Ваш отзыв успешно обновлён!')
                else:
                    messages.error(request, 'Оценка должна быть от 1 до 5.')
            except ValueError:
                messages.error(request, 'Неверный формат оценки.')
        return redirect('product_detail', product_id=review.product.id)
    return render(request, 'edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    review.product.update_average_rating()
    messages.success(request, 'Ваш отзыв успешно удалён!')
    return redirect('product_detail', product_id=product_id)