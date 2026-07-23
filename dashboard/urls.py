from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),

    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductFormView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductFormView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),

    path('returns/', views.ReturnRequestListView.as_view(), name='return_list'),
    path('returns/<int:pk>/', views.ReturnRequestDetailView.as_view(), name='return_detail'),
    path('orders/<int:order_id>/returns/add/', views.ReturnRequestCreateView.as_view(), name='return_create'),

    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employees/<int:pk>/toggle-active/', views.EmployeeToggleActiveView.as_view(), name='employee_toggle_active'),
    path('employees/<int:pk>/set-password/', views.EmployeeSetPasswordView.as_view(), name='employee_set_password'),

    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),

    path('reports/', views.ReportsView.as_view(), name='reports'),

    path('banners/', views.BannerListView.as_view(), name='banner_list'),
    path('banners/add/', views.BannerCreateView.as_view(), name='banner_create'),
    path('banners/<int:pk>/edit/', views.BannerUpdateView.as_view(), name='banner_edit'),
    path('banners/<int:pk>/delete/', views.BannerDeleteView.as_view(), name='banner_delete'),

    path('settings/', views.SiteSettingsView.as_view(), name='settings'),
]
