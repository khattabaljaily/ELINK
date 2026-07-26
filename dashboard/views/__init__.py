from .banners import BannerCreateView, BannerDeleteView, BannerListView, BannerUpdateView
from .categories import CategoryCreateView, CategoryDeleteView, CategoryListView, CategoryUpdateView
from .customers import CustomerDetailView, CustomerListView
from .employees import (
    EmployeeCreateView,
    EmployeeListView,
    EmployeeSetPasswordView,
    EmployeeToggleActiveView,
    EmployeeUpdateView,
)
from .home import DashboardHomeView
from .orders import OrderDeleteView, OrderDetailView, OrderListView
from .products import ProductDeleteView, ProductFormView, ProductListView
from .reports import ReportsView
from .returns import ReturnRequestCreateView, ReturnRequestDetailView, ReturnRequestListView
from .settings import SiteSettingsView

__all__ = [
    'DashboardHomeView',
    'ProductListView', 'ProductFormView', 'ProductDeleteView',
    'CategoryListView', 'CategoryCreateView', 'CategoryUpdateView', 'CategoryDeleteView',
    'OrderListView', 'OrderDetailView', 'OrderDeleteView',
    'ReturnRequestListView', 'ReturnRequestDetailView', 'ReturnRequestCreateView',
    'EmployeeListView', 'EmployeeCreateView', 'EmployeeUpdateView', 'EmployeeToggleActiveView', 'EmployeeSetPasswordView',
    'ReportsView',
    'SiteSettingsView',
    'CustomerListView', 'CustomerDetailView',
    'BannerListView', 'BannerCreateView', 'BannerUpdateView', 'BannerDeleteView',
]
