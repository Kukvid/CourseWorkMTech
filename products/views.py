from django.core.paginator import Paginator
from django.shortcuts import render, get_list_or_404
from products.models import *


# Create your views here.

def catalog(request, category_slug=None):
    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)
    strategies: list[IProductFilterStrategy] = []
    products = Products.objects.all()

    # Стратегия родненькая
    if query:
        strategies.append(SearchFilterStrategy(query))
    elif category_slug and category_slug != "all":
        strategies.append(CategoryFilterStrategy(category_slug))

    if on_sale:
        strategies.append(OnSaleFilterStrategy())

    if order_by and order_by != "default":
        strategies.append(OrderFilterStraregy(order_by))

    for strategy in strategies:
        products = strategy.filter(products)

    paginator = Paginator(products, 3)
    current_page = paginator.page(page)

    context = {
        "title": "MTech - Каталог",
        "products": current_page,
        "slug_url": category_slug,
    }

    return render(request, "products/catalog.html", context)

    # if category_slug == "all":
    #     products = Products.objects.all()
    # elif query:
    #     products = q_search(query)
    # else:
    #     products = get_list_or_404(Products.objects.filter(category__slug=category_slug))
    #
    # if on_sale:
    #     products = products.filter(discount__gt=0)
    #
    # if order_by and order_by != "default":
    #     products = products.order_by(order_by)


def product(request, product_slug):
    product = Products.objects.get(slug=product_slug)

    context = {
        "product": product
    }

    return render(request, "products/product.html", context)
