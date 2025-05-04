from .models import  User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Recipe

# forms.py
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'steps', 'image', 'categories', 'cooking_time']

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        for category in categories:
            if not category.parent:  # Якщо у категорії немає батька — вона головна
                raise forms.ValidationError("Рецепти можна додавати тільки в підкатегорії.")
        return categories

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Електронна пошта"
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Ім'я користувача"
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Пароль"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Підтвердження паролю"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ця електронна адреса вже використовується")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Ім'я користувача або Email"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Пароль"
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
        label="Запам'ятати мене"
    )