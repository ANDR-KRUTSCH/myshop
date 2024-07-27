from celery import shared_task

from django.core.mail import send_mail

from .models import Order

@shared_task
def order_created(order_pk: int) -> int:
    order = Order.objects.get(pk=order_pk)
    subject = f'Order nr. {order.pk}'
    message = f'Dear {order.first_name},\n\nYou have successfully placed an order. Your order ID is {order.pk}'
    mail_sent = send_mail(subject=subject, message=message, from_email=None, recipient_list=[order.email])
    return mail_sent