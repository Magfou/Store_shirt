# store/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        price = self.product.discount_price if self.product.discount_price else self.product.price
        return price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Новая модель для хранения адреса доставки и данных карты
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    city = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200, blank=True)
    house = models.CharField(max_length=50, blank=True)
    apartment = models.CharField(max_length=50, blank=True)
    card_number = models.CharField(max_length=16, blank=True, validators=[
        RegexValidator(regex=r'^\d{16}$', message='Номер карты должен состоять из 16 цифр.')
    ])
    card_expiry = models.CharField(max_length=5, blank=True, validators=[
        RegexValidator(regex=r'^(0[1-9]|1[0-2])/\d{2}$', message='Срок действия должен быть в формате MM/YY.')
    ])
    card_cvv = models.CharField(max_length=3, blank=True, validators=[
        RegexValidator(regex=r'^\d{3}$', message='CVV должен состоять из 3 цифр.')
    ])

    def __str__(self):
        return f"Profile of {self.user.username}"