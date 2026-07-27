from .banners import BannerCreateView, BannerDeleteView, BannerListView, BannerUpdateView
from .categories import CategoryCreateView, CategoryDeleteView, CategoryListView, CategoryUpdateView
from .coupons import CouponCreateView, CouponDeleteView, CouponListView, CouponUpdateView
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
from .reports import ReportsExportView, ReportsView
from .returns import ReturnRequestCreateView, ReturnRequestDetailView, ReturnRequestListView
from .reviews import ReviewDetailView, ReviewListView
from .settings import SiteSettingsView

__all__ = [
    'DashboardHomeView',
    'ProductListView', 'ProductFormView', 'ProductDeleteView',
    'CategoryListView', 'CategoryCreateView', 'CategoryUpdateView', 'CategoryDeleteView',
    'OrderListView', 'OrderDetailView', 'OrderDeleteView',
    'ReturnRequestListView', 'ReturnRequestDetailView', 'ReturnRequestCreateView',
    'EmployeeListView', 'EmployeeCreateView', 'EmployeeUpdateView', 'EmployeeToggleActiveView', 'EmployeeSetPasswordView',
    'ReportsView', 'ReportsExportView',
    'SiteSettingsView',
    'CustomerListView', 'CustomerDetailView',
    'BannerListView', 'BannerCreateView', 'BannerUpdateView', 'BannerDeleteView',
    'CouponListView', 'CouponCreateView', 'CouponUpdateView', 'CouponDeleteView',
    'ReviewListView', 'ReviewDetailView',
]
