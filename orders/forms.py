import re

from django import forms

from .models import Order

PAYMENT_METHOD_CHOICES = [
    ('cod', 'Cash on Delivery'),
    ('card', 'Card (Visa/Mastercard)'),
    ('wallet', 'Apple Pay / Google Pay'),
    ('paypal', 'PayPal'),
]

READY_PAYMENT_METHODS = {'cod'}

CARD_NUMBER_RE = re.compile(r'^\d{13,19}$')
CARD_EXPIRY_RE = re.compile(r'^(0[1-9]|1[0-2])/\d{2}$')
CARD_CVV_RE = re.compile(r'^\d{3,4}$')


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        initial='cod',
        widget=forms.RadioSelect,
    )
    card_number = forms.CharField(
        required=False, max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456', 'autocomplete': 'cc-number'}),
    )
    card_expiry = forms.CharField(
        required=False, max_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'autocomplete': 'cc-exp'}),
    )
    card_cvv = forms.CharField(
        required=False, max_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'CVV', 'autocomplete': 'cc-csc'}),
    )
    paypal_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone', 'address', 'city')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_card_number(self):
        value = self.cleaned_data.get('card_number', '')
        digits = value.replace(' ', '')
        if self.data.get('payment_method') == 'card' and not CARD_NUMBER_RE.match(digits):
            raise forms.ValidationError('Enter a valid card number.')
        return value

    def clean_card_expiry(self):
        value = self.cleaned_data.get('card_expiry', '')
        if self.data.get('payment_method') == 'card' and not CARD_EXPIRY_RE.match(value):
            raise forms.ValidationError('Use MM/YY format.')
        return value

    def clean_card_cvv(self):
        value = self.cleaned_data.get('card_cvv', '')
        if self.data.get('payment_method') == 'card' and not CARD_CVV_RE.match(value):
            raise forms.ValidationError('Enter a valid CVV.')
        return value

    def clean_paypal_email(self):
        value = self.cleaned_data.get('paypal_email', '')
        if self.data.get('payment_method') == 'paypal' and not value:
            raise forms.ValidationError('Enter your PayPal email.')
        return value

    def clean_payment_method(self):
        method = self.cleaned_data['payment_method']
        if method not in READY_PAYMENT_METHODS:
            label = dict(PAYMENT_METHOD_CHOICES)[method]
            raise forms.ValidationError(
                f'{label} isn’t linked yet — please select Cash on Delivery to complete your order.'
            )
        return method
