from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
    path('<int:order_id>/', views.order_detail, name='detail'),
]
