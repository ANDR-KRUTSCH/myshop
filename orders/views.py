import weasyprint

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.contrib.staticfiles.finders import find

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

            request.session['order_pk'] = order.pk

            return redirect(to='payment:process')
    else:
        form = OrderCreateForm()
    
    context = dict(
        cart=cart,
        form=form,
    )

    return render(request=request, template_name='orders/order/create.html', context=context)

@staff_member_required
def admin_order_detail(request: HttpRequest, order_pk: int) -> HttpResponse:
    order = get_object_or_404(klass=Order, pk=order_pk)

    context = dict(
        order=order,
    )
    
    return render(request=request, template_name='admin/orders/order/detail.html', context=context)

@staff_member_required
def admin_order_pdf(request: HttpRequest, order_pk: int) -> HttpResponse:
    order = get_object_or_404(klass=Order, pk=order_pk)

    context = dict(
        order=order,
    )

    html = render_to_string(template_name='orders/order/pdf.html', context=context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename={order.pk}.pdf'

    weasyprint.HTML(string=html).write_pdf(target=response, stylesheets=[weasyprint.CSS(find(path='css/pdf.css'))])

    return response