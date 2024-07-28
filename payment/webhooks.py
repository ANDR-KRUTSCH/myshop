import stripe

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .tasks import payment_completed
from orders.models import Order

@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    event = None
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session['mode'] == 'payment' and session['payment_status'] == 'paid':
            try:
                order = Order.objects.get(pk=session['client_reference_id'])
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            order.paid = True
            order.stripe_id = session['payment_intent']
            order.save()
            payment_completed.delay(order_pk=order.pk)
    
    return HttpResponse(status=200)