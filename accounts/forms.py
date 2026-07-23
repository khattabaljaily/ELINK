from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.text import slugify

from .models import User


class RegisterForm(UserCreationForm):
    privacy_consent = forms.BooleanField(
        required=True,
        label='I agree to the Privacy Policy and consent to my data being stored and used as described there.',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self._generate_username(user.email)
        if commit:
            user.save()
        return user

    @staticmethod
    def _generate_username(email):
        base = slugify(email.split('@')[0])[:25] or 'user'
        username = base
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f'{base}{suffix}'
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone', 'address', 'city')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or email'
        self.fields['username'].widget.attrs['placeholder'] = 'Username or email'
