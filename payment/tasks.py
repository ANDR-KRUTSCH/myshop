import weasyprint

from io import BytesIO
from celery import shared_task

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.staticfiles.finders import find

from orders.models import Order

@shared_task
def payment_completed(order_pk: int) -> int:
    order = Order.objects.get(pk=order_pk)

    subject = f'My Shop - Invoice no. {order.pk}'
    message = f'Please, find attached the invoice for your recent purchase.'

    email = EmailMessage(subject=subject, body=message, from_email=None, to=[order.email])

    context = dict(
        order=order,
    )

    html = render_to_string(template_name='orders/order/pdf.html', context=context)
    out = BytesIO()

    weasyprint.HTML(string=html).write_pdf(target=out, stylesheets=[weasyprint.CSS(find(path='css/pdf.css'))])

    email.attach(filename=f'order_{order.pk}.pdf', content=out.getvalue(), mimetype='application/pdf')

    email.send()