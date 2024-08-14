from django import forms

class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    height = forms.FloatField(required=True)
    weight = forms.FloatField(required=True)