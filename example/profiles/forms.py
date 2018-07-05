import time
import uuid

from django import forms
from django.contrib.auth.models import User

from example.profiles.models import Profile


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['about_me']


class PublishingProfileForm(forms.ModelForm):

    error_messages = {
        'duplicate_username': 'A user with that username already exists.',
        'duplicate_email': 'A user with that e-mail already exists.',
        'password_mismatch': 'The two password fields didn\'t match.',
    }
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), help_text='Enter the same password as above, for verification.')

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'about_me', 'user_role')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2


class PublishingProfileCreateForm(PublishingProfileForm):

    pass


class PublishingProfileUpdateForm(PublishingProfileForm):

    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), help_text='Enter the same password as above, for verification.', required=False)

    def clean_email(self):
        return self.cleaned_data['email']


class SignupForm(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()

    def save(self, user):
        user.username = uuid.uuid4().hex[:20] + str(time.time()).split('.')[0]
        user.save()
