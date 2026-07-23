from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Order, ReturnRequest

# Card/PayPal/wallet checkout isn't wired to a PCI-compliant payment gateway yet,
# so the form only ever collects Cash on Delivery — no cardholder data touches
# our server. Add the other methods here once a real gateway (e.g. Stripe
# Elements, PayPal Checkout) is integrated.
PAYMENT_METHOD_CHOICES = [
    ('cod', 'Cash on Delivery'),
    ('card', 'Card (Visa/Mastercard) — coming soon'),
    ('wallet', 'Apple Pay / Google Pay — coming soon'),
    ('paypal', 'PayPal — coming soon'),
]

READY_PAYMENT_METHODS = {'cod'}


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        initial='cod',
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone', 'address', 'city')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_payment_method(self):
        method = self.cleaned_data['payment_method']
        if method not in READY_PAYMENT_METHODS:
            label = dict(PAYMENT_METHOD_CHOICES)[method]
            raise forms.ValidationError(
                f'{label} isn’t linked yet — please select Cash on Delivery to complete your order.'
            )
        return method


class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ('reason', 'resolution_requested', 'description')
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add any details that will help us process this quickly.',
            }),
        }

    def __init__(self, *args, order=None, **kwargs):
        self.order = order
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get('reason')
        resolution = cleaned_data.get('resolution_requested')

        if self.order is not None and reason and resolution:
            if not self.order.delivered_at:
                raise forms.ValidationError(
                    'This order hasn’t been marked as delivered yet, so a return can’t be requested.'
                )

            elapsed = timezone.now() - self.order.delivered_at
            if reason in (ReturnRequest.Reason.DAMAGED, ReturnRequest.Reason.DEFECTIVE):
                window, window_label = timedelta(hours=24), '24 hours'
            elif resolution == ReturnRequest.Resolution.REFUND:
                window, window_label = timedelta(days=3), '3 days'
            else:
                window, window_label = timedelta(days=7), '7 days'

            if elapsed > window:
                raise forms.ValidationError(
                    f'The window to request this ({window_label} after delivery) has passed. '
                    'Please contact support directly for help.'
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.order = self.order
        if commit:
            instance.save()
        return instance
