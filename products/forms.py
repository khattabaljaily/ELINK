from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'body')
        widgets = {
            'rating': forms.RadioSelect(),
            'title': forms.TextInput(attrs={'placeholder': 'Sum up your experience (optional)'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What did you like or dislike?'}),
        }
