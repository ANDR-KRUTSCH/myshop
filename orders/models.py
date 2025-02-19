from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from shop.models import Product
from coupons.models import Coupon

# Create your models here.
class Order(models.Model):
    first_name = models.CharField(verbose_name=_(message='first name'), max_length=50)
    last_name = models.CharField(verbose_name=_(message='last name'), max_length=50)
    email = models.EmailField(verbose_name=_(message='email'), )
    address = models.CharField(verbose_name=_(message='address'), max_length=250)
    postal_code = models.CharField(verbose_name=_(message='postal code'), max_length=20)
    city = models.CharField(verbose_name=_(message='city'), max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(to=Coupon, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    discount = models.IntegerField(default=0, validators=[MinValueValidator(limit_value=0), MaxValueValidator(limit_value=100)])

    class Meta:
        ordering = (
            '-created',
        )
        indexes = (
            models.Index(
                fields=(
                    '-created',
                )
            ),
        )

    def __str__(self) -> str:
        return f'Order {self.pk}'
    
    def get_total_cost_before_discount(self) -> Decimal:
        return sum(item.get_cost() for item in self.items.all())
    
    def get_discount(self) -> Decimal:
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return self.discount / Decimal(100) * total_cost
        return Decimal(0)
    
    def get_total_cost(self) -> Decimal:
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()
    
    def get_stripe_url(self) -> str:
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return str(self.pk)
    
    def get_cost(self) -> Decimal:
        return self.price * self.quantity