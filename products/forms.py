from django import forms

from .models import Review, Variant


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'body')
        widgets = {
            'rating': forms.RadioSelect(),
            'title': forms.TextInput(attrs={'placeholder': 'Sum up your experience (optional)'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What did you like or dislike?'}),
        }


class StockSubscriptionForm(forms.Form):
    variant = forms.ModelChoiceField(queryset=Variant.objects.all(), widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your email'}))
