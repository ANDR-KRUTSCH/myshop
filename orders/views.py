from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from cart.cart import Cart
from .tasks import order_created
from .forms import OrderCreateForm
from .models import Order, OrderItem

# Create your views here.
def order_create(request: HttpRequest) -> HttpResponse:
    cart = Cart(request=request)

    if request.method == 'POST':
        form = OrderCreateForm(data=request.POST)
        if form.is_valid():
            order: Order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            order_created.delay(order_pk=order.pk)

            context = dict(
                order=order,
            )

            return render(request=request, template_name='orders/order/created.html', context=context)
    else:
        form = OrderCreateForm()
    
    context = dict(
        cart=cart,
        form=form,
    )

    return render(request=request, template_name='orders/order/create.html', context=context)