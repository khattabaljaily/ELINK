from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cart.api import CartAddItemView, CartDetailView, CartRemoveItemView, CartUpdateItemView
from products.api import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')

api_urlpatterns = [
    path('', include(router.urls)),
    path('cart/', CartDetailView.as_view(), name='api-cart-detail'),
    path('cart/add/', CartAddItemView.as_view(), name='api-cart-add'),
    path('cart/items/<int:item_id>/update/', CartUpdateItemView.as_view(), name='api-cart-update'),
    path('cart/items/<int:item_id>/remove/', CartRemoveItemView.as_view(), name='api-cart-remove'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
