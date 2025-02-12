from django import forms
from .models import Domains

class DomainForm(forms.ModelForm):
    class Meta:
        model = Domains
        fields = ['domain_suffix']