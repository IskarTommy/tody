from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# This form will be used for the signup page
class SignupForm(UserCreationForm):
    # We add the fields we want to the standard UserCreationForm
    email = forms.EmailField(max_length=254, required=True, help_text='Required. A valid email address.')
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

# This form will be used for the login page
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)