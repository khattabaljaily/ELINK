from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from orders.models import Order

from .forms import EmailOrUsernameAuthenticationForm, ProfileForm, RegisterForm


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('dashboard:home')
        return super().get_default_redirect_url()


class AccountLogoutView(LogoutView):
    next_page = 'products:list'


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('products:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class AccountPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been updated.')
        return response


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def my_orders(request):
    orders = list(
        Order.objects.filter(user=request.user)
        .prefetch_related('return_requests')
        .order_by('-created_at')
    )
    for order in orders:
        order.open_return = next(
            (r for r in order.return_requests.all() if r.status in ('pending', 'approved')), None,
        )
    return render(request, 'accounts/orders.html', {'orders': orders})
