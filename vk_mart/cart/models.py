from django.db import models
from django.contrib.auth.models import User
from core.models import Product


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='cart_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='cart_reviews')
    comment = models.TextField()
    rate = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()


class CouponCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='cart_orders')
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postalcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    additional_info = models.TextField(blank=True, null=True)
    payment_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.CharField(max_length=200)
    image = models.ImageField(upload_to="order_items/")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
