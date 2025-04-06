# store/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Order

@receiver(post_save, sender=Order)
def send_order_status_update(sender, instance, created, **kwargs):
    if not created:  # Отправляем email только при обновлении, а не при создании
        subject = f'Обновление статуса заказа #{instance.id}'
        if instance.status == 'SHIPPED':
            message = f'Ваш заказ #{instance.id} был отправлен! Ожидайте доставку.'
        elif instance.status == 'DELIVERED':
            message = f'Ваш заказ #{instance.id} доставлен! Спасибо за покупку!'
        elif instance.status == 'CANCELLED':
            message = f'Ваш заказ #{instance.id} был отменён.'
        else:
            return  # Не отправляем email для статуса PENDING

        send_mail(
            subject,
            message,
            'from@example.com',
            [instance.user.email],
            fail_silently=False,
        )