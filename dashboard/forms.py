from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

from orders.models import Order
from products.models import Category, Product, ProductImage, Variant

from .models import SiteSettings

User = get_user_model()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'category', 'description', 'price', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def clean_name(self):
        name = self.cleaned_data['name']
        qs = Product.objects.filter(slug=slugify(name))
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A product with this name already exists.')
        return name


class BaseProductImageFormSet(forms.BaseInlineFormSet):
    """Only one image can be primary — if more than one is checked
    (e.g. JS was bypassed), keep the first and unset the rest."""

    def clean(self):
        super().clean()
        primary_forms = [
            form for form in self.forms
            if getattr(form, 'cleaned_data', None)
            and not form.cleaned_data.get('DELETE')
            and form.cleaned_data.get('is_primary')
        ]
        for form in primary_forms[1:]:
            form.cleaned_data['is_primary'] = False
            form.instance.is_primary = False


ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage,
    fields=('image', 'alt_text', 'is_primary'),
    formset=BaseProductImageFormSet,
    extra=0, can_delete=True,
)

VariantFormSet = forms.inlineformset_factory(
    Product, Variant,
    fields=('size', 'color', 'sku', 'stock', 'price_override'),
    extra=1, can_delete=True,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')

    def clean_name(self):
        name = self.cleaned_data['name']
        qs = Category.objects.filter(slug=slugify(name))
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A category with this name already exists.')
        return name


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status',)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if not (user and user.is_superuser):
            self.fields['status'].choices = [
                choice for choice in self.fields['status'].choices
                if choice[0] != Order.Status.CANCELLED
            ]

    def clean_status(self):
        status = self.cleaned_data['status']
        if status == Order.Status.CANCELLED and not (self.user and self.user.is_superuser):
            raise forms.ValidationError('Only a superuser can cancel an order.')
        return status


class EmployeeCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ('maintenance_mode', 'coming_soon_message')
        widgets = {'coming_soon_message': forms.Textarea(attrs={'rows': 4})}
