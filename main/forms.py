from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from . import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = models.Enquiry
        fields = ('full_name','email','detail')
        widgets = {
            "full_name": forms.TextInput(attrs={"class":"form-control",}),
            "email":forms.EmailInput(attrs={"class":"form-control",}),
            "detail":forms.Textarea(attrs={"class":"form-control","rows":"2"}),
        }

class SignUp(UserCreationForm):
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    phone_number = forms.CharField(
        label=_("Phone Number"),
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "username": None,
            "password1": None,
            "password2": None,
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Basic phone number validation using regex
        if not re.match(r'^\+?1?\d{11,13}$',str(phone_number or '')):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super(SignUp, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            phone_number = self.cleaned_data['phone_number']
            user.userprofile.phone_number = phone_number
            user.userprofile.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'})
        }


class ProfileForm(UserChangeForm):
    phone_number = forms.CharField(
        label="Phone Number",
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number')
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'userprofile'):
            self.fields['phone_number'].initial = self.instance.userprofile.phone_number

    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'userprofile'):
                user.userprofile.phone_number = self.cleaned_data['phone_number']
                user.userprofile.save()
        return user
     
class TrainerLoginForm(forms.ModelForm):
     class Meta:
          model=models.Trainer
          fields=('username','pwd')
          widgets = {
               'pwd': forms.PasswordInput(attrs={'class': 'form-control'}),
               'username': forms.TextInput(attrs={'class': 'form-control'}),
          }


class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model=models.Trainer
        fields=('full_name','mobile','address','detail','img')
        widgets = {
            'full_name': forms.TextInput(attrs={"class":"form-control"}),
            'mobile': forms.TextInput(attrs={"class":"form-control"}),
            'address': forms.Textarea(attrs={"class":"form-control"}),
            'detail': forms.Textarea(attrs={"class":"form-control"}),
            # 'img': forms.ImageField(attrs={"class":"form-control"}),
            }

class TrainerChangePassword(forms.Form):
    new_password=forms.CharField(max_length=50,required=True,widget=forms.PasswordInput(attrs={"class": "form-control"}))

class ReportForUserForm(forms.ModelForm):
	class Meta:
		model=models.TrainerSubscriberReport
		fields=('report_for_user','report_msg','report_from_trainer')
		widgets = {'report_from_trainer': forms.HiddenInput()}

class ReportForTrainerForm(forms.ModelForm):
	class Meta:
		model=models.TrainerSubscriberReport
		fields=('report_for_trainer','report_msg','report_from_user')
		widgets = {'report_from_user': forms.HiddenInput()}


