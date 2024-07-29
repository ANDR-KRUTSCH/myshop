import stripe

from decimal import Decimal

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse

from orders.models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

# Create your views here.
def payment_process(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    order_pk = request.session['order_pk']
    order = get_object_or_404(klass=Order, pk=order_pk)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(location=reverse(viewname='payment:completed'))
        cancel_url = request.build_absolute_uri(location=reverse(viewname='payment:canceled'))

        line_items = list()

        for item in order.items.all():
            item: OrderItem = item
            line_items.append(
                {
                    'price_data': {
                        'unit_amount': int(item.price) * Decimal('100'),
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        }
                    },
                    'quantity': item.quantity,
                }
            )

        if order.coupon:
            stripe_coupon = stripe.Coupon.create(name=order.coupon.code, percent_off=order.discount, duration='once')

        session = stripe.checkout.Session.create(
            mode='payment',
            client_reference_id=order.pk,
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=line_items,
            discounts=[dict(coupon=stripe_coupon.id)]
        )

        return redirect(to=session.url, code=303)
    else:
        return render(request=request, template_name='payment/process.html', context=locals())
    
def payment_completed(request: HttpRequest) -> HttpResponse:
    return render(request=request, template_name='payment/completed.html')

def payment_canceled(request: HttpRequest) -> HttpResponse:
    return render(request=request, template_name='payment/canceled.html')