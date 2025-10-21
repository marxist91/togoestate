from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Agency

class AgencyCreateForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ['name', 'email', 'phone', 'city', 'address', 'description', 'logo_url']

class SignUpForm(UserCreationForm):
    #role = forms.ChoiceField(choices=User.Roles.choices, initial=User.Roles.CUSTOMER)
    agency = forms.ModelChoiceField(queryset=Agency.objects.all(), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email',  'agency')

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))