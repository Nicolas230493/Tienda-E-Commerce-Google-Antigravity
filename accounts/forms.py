from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('name', 'recipient_name', 'street_address', 'city', 'state', 'postal_code', 'country', 'is_default')
