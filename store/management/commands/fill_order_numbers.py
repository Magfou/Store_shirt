from django.core.management.base import BaseCommand 
from store.models import Order 
import time 
 
class Command(BaseCommand): 
    help = 'Fill user_order_number for existing orders' 
 
    def handle(self, *args, **kwargs): 
        orders = Order.objects.filter(user_order_number='') 
        for order in orders: 
            order.user_order_number = f"ORD-{order.id}-{int(order.created_at.timestamp())}" 
            order.save() 
