from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from coupons.models import Coupon

from ..forms import CouponForm
from ..mixins import AjaxDeleteMixin, AjaxFormMixin
from ..permissions import ManagerRequiredMixin, SuperuserRequiredMixin


class CouponListView(ManagerRequiredMixin, ListView):
    template_name = 'dashboard/coupons/list.html'
    context_object_name = 'coupons'

    def get_queryset(self):
        return Coupon.objects.order_by('-created_at')


class CouponCreateView(AjaxFormMixin, ManagerRequiredMixin, CreateView):
    model = Coupon
    form_class = CouponForm
    template_name = 'dashboard/coupons/form.html'
    partial_template_name = 'dashboard/coupons/_form_fields.html'
    success_url = reverse_lazy('dashboard:coupon_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Coupon "{self.object.code}" created.')
        return response


class CouponUpdateView(AjaxFormMixin, ManagerRequiredMixin, UpdateView):
    model = Coupon
    form_class = CouponForm
    template_name = 'dashboard/coupons/form.html'
    partial_template_name = 'dashboard/coupons/_form_fields.html'
    success_url = reverse_lazy('dashboard:coupon_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Coupon "{self.object.code}" updated.')
        return response


class CouponDeleteView(AjaxDeleteMixin, SuperuserRequiredMixin, DeleteView):
    model = Coupon
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:coupon_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Delete coupon "{self.object.code}"?'
        ctx['cancel_url'] = reverse_lazy('dashboard:coupon_list')
        return ctx
