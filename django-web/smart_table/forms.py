from django import forms

class LoginForm(forms.Form):
    nis = forms.CharField(max_length=30, label="NIS")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")