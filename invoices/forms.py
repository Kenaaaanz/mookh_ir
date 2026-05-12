from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Invoice, Report


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.is_active = True
            user.save()
            # Save phone to profile
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.save()
        return user


class InvoiceForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))

    class Meta:
        model = Invoice
        fields = ['event_name', 'event_date', 'shifts_covered', 'amount_to_be_paid', 'notes']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-input'}),
            'shifts_covered': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'amount_to_be_paid': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['event_name', 'location', 'general_report', 'tech_report', 'additional_notes']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'general_report': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'tech_report': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
