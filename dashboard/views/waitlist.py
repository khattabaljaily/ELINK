from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import FormView

from ..forms import WaitlistSignupForm


class WaitlistSignupView(FormView):
    """Public 'notify me' capture, reachable even while maintenance mode is on."""

    form_class = WaitlistSignupForm

    def get(self, request, *args, **kwargs):
        return redirect('/')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "You're on the list — we'll email you the moment we launch.")
        return redirect('/')

    def form_invalid(self, form):
        if 'email' in form.errors and 'unique' in ''.join(e.code or '' for e in form.errors.as_data().get('email', [])):
            messages.info(self.request, "You're already on the list.")
        else:
            messages.error(self.request, 'Please enter a valid email address.')
        return redirect('/')
