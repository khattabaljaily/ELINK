from django.core.paginator import Paginator
from django.db.models import Count, F, Window
from django.db.models.functions import RowNumber
from django.shortcuts import get_object_or_404, render

from .filters import ProductFilter
from .models import Category, Product

PRODUCTS_PER_PAGE = 24
PRODUCTS_PER_ROW = 5


def product_list(request, slug=None):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    search_query = request.GET.get('q', '')
    is_filtered = bool(search_query or request.GET.get('min_price') or request.GET.get('max_price'))

    context = {
        'categories': Category.objects.all(),
        'category': category,
        'search_query': search_query,
    }

    if not category and not is_filtered:
        # Browsing the full catalog with no filters - group by category, one row
        # each, with a link through to the category's own paginated page.
        #
        # Ranks every active product within its own category by recency in a
        # single query (instead of one query per category), then keeps the
        # top PRODUCTS_PER_ROW + 1 of each - the "+1" is just to detect
        # whether there's more to show without a separate count query.
        ranked = Product.objects.filter(is_active=True).annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F('category_id')],
                order_by=F('created_at').desc(),
            ),
        )
        top_products = (
            ranked.filter(row_number__lte=PRODUCTS_PER_ROW + 1)
            .select_related('category').prefetch_related('images', 'variants')
            .order_by('category_id', 'row_number')
        )

        by_category = {}
        for product in top_products:
            by_category.setdefault(product.category_id, []).append(product)

        counts = dict(
            Category.objects.filter(products__is_active=True)
            .annotate(product_count=Count('products')).values_list('id', 'product_count'),
        )

        sections = []
        for cat in context['categories']:
            cat_products = by_category.get(cat.id, [])
            if not cat_products:
                continue
            sections.append({
                'category': cat,
                'product_count': counts.get(cat.id, 0),
                'products': cat_products[:PRODUCTS_PER_ROW],
                'has_more': len(cat_products) > PRODUCTS_PER_ROW,
            })
        context['sections'] = sections
        return render(request, 'products/list.html', context)

    filtered = ProductFilter(request.GET, queryset=products)

    paginator = Paginator(filtered.qs, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    querystring = request.GET.copy()
    querystring.pop('page', None)

    context.update({
        'products': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'querystring': querystring.urlencode(),
    })
    return render(request, 'products/list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'variants'),
        slug=slug, is_active=True,
    )
    return render(request, 'products/detail.html', {'product': product})
