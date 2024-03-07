from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User
from django import forms
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
)


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
        
        def username_check(self):
            username = self.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken. Please choose a different one.")
            return username
        
        def password_check(self):
            cleaned_data = super().clean()
            password1 = cleaned_data.get('password1')
            password2 = cleaned_data.get('password2')

            # Run the default password validation
            validators = [MinimumLengthValidator(), CommonPasswordValidator()]
            for validator in validators:
                validator(password1, self)

            # Add custom validation for similarity to personal information
            if password1 and password1.lower() in cleaned_data.get('name').lower():
                raise forms.ValidationError(
                    "Password is too similar to your personal information."
                )

            # Add custom validation for minimum length
            if len(password1) < 8:
                raise forms.ValidationError(
                    "Password must contain at least 8 characters."
                )

            # Add custom validation for password match
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

            return cleaned_data
        
        def email_check(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email address is already in use.")
            return email
        


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = [
            'host', 'participants'
        ]

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio', 'date_of_birth', 'location']