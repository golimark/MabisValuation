from django import forms
from .models import *
from accounts.models import *
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
from accounts.models import *
from django.db.models import Q


class LoanCompanyForm(forms.ModelForm):
    class Meta:
        model = LoanCompany
        fields = ['name', 'api']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field_name, field in self.fields.items():
                field.widget.attrs.update({'class': 'form-control'})

class ActiveLoanCompanyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["active_company"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})



class UserActiveCompanyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["active_company"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "role", "company", "status", "image"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        if user:
            self.fields['role'].queryset = Role.objects.filter(company=user.company)
            self.fields['company'].initial = user.company

    def add_password_button(self):
        return mark_safe('<button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#passwordChangeModal">Change Password</button>')

class PasswordChangeForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["new_password", "confirm_password"]

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data



# Change own passwd
class ChangePasswordForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password",
        required=True
    )

    class Meta:
        model = User
        fields = []  # No other fields included

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
        if commit:
            user.save()
        return user

#change users' passwd
class AdminPasswordChangeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="New Password")

    class Meta:
        model = User
        fields = ['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserCreateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "role", "company", "status", "password", "image"]
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        fields = ["first_name", "last_name", "username", "email", "role", "company", "status", "password", "image"]

        for field in fields:
            self.fields[field].required = True

        # Set required attribute for 'image' field
        self.fields['image'].required = True


        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            if user:
                self.fields['role'].queryset = Role.objects.filter(company=user.company)
                self.fields['company'].initial = user.company

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        exclude = ["permissions","created_at","update_at","slug", 'company']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})




class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','code' ,'logo', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company code'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company address'}),
        }




class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label="Enter your email", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))