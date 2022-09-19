from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext, gettext_lazy as _

from posts.models import CustomUser


class AccountForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'avatar')

        labels = {
            'username': ('Никнэйм'),
            'first_name': ('Имя'),
            'last_name': ('Фамилия'),
            'email': ('e-mail'),
            'avatar': ('аватар'),
        }
        help_texts = {
            'username': ('Введите имя пользователя в системе'),
            'first_name': ('Имя'),
            'last_name': ('Фамилия'),
            'email': ('Адрес электронной почты'),
            'avatar': ('Вставьте аватар'),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('e-mail/Имя'),
        strip=False,
        widget=forms.TextInput,
    )


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'last_name', 'first_name', 'username')
