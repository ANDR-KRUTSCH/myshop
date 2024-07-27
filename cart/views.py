from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm

# Create your views here.
@require_POST
def cart_add(request: HttpRequest, product_pk: int) -> HttpResponseRedirect:
    cart = Cart(request=request)
    product = get_object_or_404(klass=Product, pk=product_pk, available=True)

    form = CartAddProductForm(data=request.POST)
    if form.is_valid():
        cart.add(product=product, quantity=form.cleaned_data.get('quantity'), override_quantity=form.cleaned_data.get('override'))
    
    return redirect(to='cart:cart_detail')

@require_POST
def cart_remove(request: HttpRequest, product_pk: int) -> HttpResponseRedirect:
    cart = Cart(request=request)
    product = get_object_or_404(klass=Product, pk=product_pk)
    
    cart.remove(product=product)
    
    return redirect(to='cart:cart_detail')

def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request=request)

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial=dict(quantity=item['quantity'], override=True))

    context = dict(
        cart=cart,
    )

    return render(request=request, template_name='cart/detail.html', context=context)