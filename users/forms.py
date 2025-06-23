from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom form for registering a new user using a custom User model."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your last name'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a username'
    }))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create a password'
    }))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repeat your password'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing basic user account information."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("This email address is already in use.")
        return email


class ProfileEditForm(forms.ModelForm):
    """Form for editing user's additional profile information."""

    class Meta:
        model = Profile
        fields = [
            'avatar', 'phone', 'bio', 'address',
            'city', 'state', 'dietary_preferences', 'favorite_flavors'
        ]
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'placeholder': 'Enter your phone number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us a little about yourself...'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your state or region'
            }),
            'dietary_preferences': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Vegetarian, Vegan, Gluten-free'
            }),
            'favorite_flavors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chocolate, Vanilla, Strawberry'
            }),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            max_size = 5 * 1024 * 1024  # 5MB
            if avatar.size > max_size:
                raise forms.ValidationError("Image file too large (maximum 5MB allowed).")
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                raise forms.ValidationError("Invalid image format. Use JPEG, PNG, or GIF.")
        return avatar
