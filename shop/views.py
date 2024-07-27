from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from cart.forms import CartAddProductForm
from .models import Category, Product

# Create your views here.
def product_list(request: HttpRequest, category_slug: str = None) -> HttpResponse:
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(klass=Category, slug=category_slug)
        products = products.filter(category=category)

    context = dict(
        category=category,
        categories=categories,
        products=products,
    )

    return render(request=request, template_name='shop/product/list.html', context=context)

def product_detail(request: HttpRequest, pk: int, slug: str) -> HttpResponse:
    product = get_object_or_404(klass=Product, pk=pk, slug=slug, available=True)

    context = dict(
        product=product,
        cart_product_form=CartAddProductForm(),
    )

    return render(request=request, template_name='shop/product/detail.html', context=context)