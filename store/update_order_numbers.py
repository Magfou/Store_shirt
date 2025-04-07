# update_order_numbers.py
from django.contrib.auth.models import User
from store.models import Order

def update_order_numbers():
    # Получаем всех пользователей
    users = User.objects.all()
    for user in users:
        # Получаем все заказы пользователя, отсортированные по created_at
        orders = Order.objects.filter(user=user).order_by('created_at')
        # Присваиваем номера, начиная с 1
        for index, order in enumerate(orders, start=1):
            order.order_number = index
            order.save()

if __name__ == "__main__":
    update_order_numbers()