from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email')
