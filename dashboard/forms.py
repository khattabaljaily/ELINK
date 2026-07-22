from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify

from orders.models import Order
from products.models import Category, Product, ProductImage, Variant

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


ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage,
    fields=('image', 'alt_text', 'is_primary'),
    extra=1, can_delete=True,
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
