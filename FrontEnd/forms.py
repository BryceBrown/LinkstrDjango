from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

class SignupFormRecaptcha(forms.Form):
	Username = forms.CharField(required=True, validators=[
			RegexValidator('^[0-9a-zA-Z]*$', message='Usernames can only contain numbers and letters'),
            MinLengthValidator(4),
            MaxLengthValidator(14)])
	ReEnterPassword = forms.CharField(required=True)
	Email = forms.EmailField(required=True)
	Password = forms.CharField(required=True, validators=[MinLengthValidator(6), MaxLengthValidator(20)])
	NewsLetter = forms.BooleanField(required=False)

	def clean(self):
		password1 = self.cleaned_data.get('Password')
		password2 = self.cleaned_data.get('ReEnterPassword')

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match", code='Passwords')

		#Make sure username is unique
		username = self.cleaned_data.get('Username')
		if User.objects.filter(username=username).count() > 0:
			raise forms.ValidationError("Username is already in use", code='Username')

		#make sure password is unique
		email = self.cleaned_data.get('Email')
		if User.objects.filter(email=email).count() > 0:
			raise forms.ValidationError("Email is already in use", code='Email')

		return self.cleaned_data

	def createUser(self):
		return User.objects.create_user(self.cleaned_data['Username'], self.cleaned_data['Email'], self.cleaned_data['Password'])
