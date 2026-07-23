from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.AccountLoginView.as_view(), name='login'),
    path('logout/', views.AccountLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.my_orders, name='orders'),
    path('password/', views.AccountPasswordChangeView.as_view(), name='password_change'),
]
