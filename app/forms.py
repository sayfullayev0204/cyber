
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User,Group,Channel,BotToken

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'role']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = '__all__'

class BotTokenForm(forms.ModelForm):
    class Meta:
        model = BotToken
        fields = ['token']
        widgets = {
            'token': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Bot Token'}),
        }
