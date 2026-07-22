from django.shortcuts import get_object_or_404, render

from .filters import ProductFilter
from .models import Category, Product


def product_list(request, slug=None):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    filtered = ProductFilter(request.GET, queryset=products)

    context = {
        'products': filtered.qs,
        'categories': Category.objects.all(),
        'category': category,
        'search_query': request.GET.get('q', ''),
    }
    return render(request, 'products/list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'variants'),
        slug=slug, is_active=True,
    )
    return render(request, 'products/detail.html', {'product': product})
