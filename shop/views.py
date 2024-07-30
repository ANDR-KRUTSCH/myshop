from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from cart.forms import CartAddProductForm
from . import recommender
from .models import Category, Product

# Create your views here.
def product_list(request: HttpRequest, category_slug: str = None) -> HttpResponse:
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        language = request.LANGUAGE_CODE
        category = get_object_or_404(klass=Category, translations__language_code=language, translations__slug=category_slug)
        products = products.filter(category=category)

    context = dict(
        category=category,
        categories=categories,
        products=products,
    )

    return render(request=request, template_name='shop/product/list.html', context=context)

def product_detail(request: HttpRequest, pk: int, slug: str) -> HttpResponse:
    language = request.LANGUAGE_CODE
    product = get_object_or_404(klass=Product, pk=pk, translations__language_code=language, translations__slug=slug, available=True)

    my_recommender = recommender.Recommender()
    recommended_products = my_recommender.suggest_products_for(products=[product], max_results=4)

    context = dict(
        product=product,
        recommended_products=recommended_products,
        cart_product_form=CartAddProductForm(),
    )

    return render(request=request, template_name='shop/product/detail.html', context=context)