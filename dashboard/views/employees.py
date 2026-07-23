from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from ..forms import EmployeeCreateForm, EmployeeUpdateForm
from ..mixins import AjaxFormMixin, is_ajax
from ..permissions import ManagerRequiredMixin, SuperuserRequiredMixin

User = get_user_model()


class EmployeeListView(ManagerRequiredMixin, ListView):
    template_name = 'dashboard/employees/list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return User.objects.filter(is_staff=True).order_by('-is_active', 'username')


class EmployeeCreateView(AjaxFormMixin, ManagerRequiredMixin, CreateView):
    model = User
    form_class = EmployeeCreateForm
    template_name = 'dashboard/employees/form.html'
    partial_template_name = 'dashboard/employees/_form_fields.html'
    success_url = reverse_lazy('dashboard:employee_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Employee "{self.object.username}" created.')
        return response


class EmployeeUpdateView(AjaxFormMixin, ManagerRequiredMixin, UpdateView):
    model = User
    form_class = EmployeeUpdateForm
    template_name = 'dashboard/employees/form.html'
    partial_template_name = 'dashboard/employees/_form_fields.html'
    success_url = reverse_lazy('dashboard:employee_list')

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Employee "{self.object.username}" updated.')
        return response


class EmployeeSetPasswordView(SuperuserRequiredMixin, View):
    partial_template_name = 'dashboard/employees/_set_password_fields.html'

    def get_employee(self, pk):
        return get_object_or_404(User, pk=pk, is_staff=True)

    def get(self, request, pk):
        employee = self.get_employee(pk)
        form = SetPasswordForm(employee)
        context = {'employee': employee, 'form': form}
        if is_ajax(request):
            return render(request, self.partial_template_name, context)
        return render(request, 'dashboard/employees/set_password.html', context)

    def post(self, request, pk):
        employee = self.get_employee(pk)
        form = SetPasswordForm(employee, request.POST)
        if form.is_valid():
            form.save()
            if is_ajax(request):
                return JsonResponse({'success': True})
            messages.success(request, f'Password updated for "{employee.username}".')
            return redirect('dashboard:employee_list')

        context = {'employee': employee, 'form': form}
        if is_ajax(request):
            return render(request, self.partial_template_name, context, status=400)
        return render(request, 'dashboard/employees/set_password.html', context)


class EmployeeToggleActiveView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        employee = get_object_or_404(User, pk=pk, is_staff=True)
        if employee == request.user:
            if is_ajax(request):
                return JsonResponse({'success': False, 'error': "You can't deactivate your own account."}, status=400)
            messages.error(request, "You can't deactivate your own account.")
        else:
            employee.is_active = not employee.is_active
            employee.save(update_fields=['is_active'])
            state = 'activated' if employee.is_active else 'deactivated'
            if is_ajax(request):
                return JsonResponse({'success': True})
            messages.success(request, f'Employee "{employee.username}" {state}.')
        return redirect('dashboard:employee_list')
