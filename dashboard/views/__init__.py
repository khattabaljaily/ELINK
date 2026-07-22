from .categories import CategoryCreateView, CategoryDeleteView, CategoryListView, CategoryUpdateView
from .employees import EmployeeCreateView, EmployeeListView, EmployeeToggleActiveView, EmployeeUpdateView
from .home import DashboardHomeView
from .orders import OrderDeleteView, OrderDetailView, OrderListView
from .products import ProductDeleteView, ProductFormView, ProductListView
from .reports import ReportsView
from .settings import SiteSettingsView

__all__ = [
    'DashboardHomeView',
    'ProductListView', 'ProductFormView', 'ProductDeleteView',
    'CategoryListView', 'CategoryCreateView', 'CategoryUpdateView', 'CategoryDeleteView',
    'OrderListView', 'OrderDetailView', 'OrderDeleteView',
    'EmployeeListView', 'EmployeeCreateView', 'EmployeeUpdateView', 'EmployeeToggleActiveView',
    'ReportsView',
    'SiteSettingsView',
]
