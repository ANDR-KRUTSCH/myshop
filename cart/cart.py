from decimal import Decimal

from django.http import HttpRequest
from django.conf import settings

from shop.models import Product

class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = dict()
        self.cart = cart
    
    def save(self) -> None:
        self.session.modified = True

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        product_pk = str(product.pk)
        if product_pk not in self.cart:
            self.cart[product_pk] = dict(
                quantity=0,
                price=str(product.price),
            )
        if override_quantity:
            self.cart[product_pk]['quantity'] = quantity
        else:
            self.cart[product_pk]['quantity'] += quantity
        self.save()

    def remove(self, product: Product) -> None:
        product_pk = str(product.pk)
        if product_pk in self.cart:
            del self.cart[product_pk]
            self.save()

    def get_total_price(self) -> Decimal:
        return sum(item['quantity'] * Decimal(item['price']) for item in self.cart.values())
    
    def clear(self) -> None:
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(pk__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.pk)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(value=item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        return sum(item['quantity'] for item in self.cart.values())