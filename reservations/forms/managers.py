from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth.models import User
from reservations.models import ManagerProfile

class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True, error_messages={ 'required': "Please give an email!", 'invalid': "The email you entered is invalid! Try again!" })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].error_messages['required'] = "Please give a username!"
        self.fields['password1'].error_messages['required'] = "Please give a password!"
        self.fields['password2'].error_messages['required'] = "Please confirm the password!"

class CreateManagerForm(CreateUserForm):
    teams = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_active=True, groups__name='Team'), required=False)

    def save(self):
        user = super(CreateManagerForm, self).save()

        manager_profile = ManagerProfile(user=user)
        manager_profile.save()
        manager_profile.teams.set(self.cleaned_data.get('teams'))

        user.change_group('Manager')

        return user

class CreateSuperuserForm(CreateUserForm):
    def save(self):
        user = super(CreateSuperuserForm, self).save(commit=False)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        user.change_group('Superuser')

        return user
