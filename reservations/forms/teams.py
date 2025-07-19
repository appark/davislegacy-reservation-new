from django.forms import ModelForm
from django import forms
import string, random

from django.contrib.auth.models import User
from reservations.models import TeamProfile, GENDER_CHOICES

class CreateTeamForm(ModelForm):
    description = forms.CharField(max_length=2048, required=False, error_messages={
        'max_length': "The description is too long. Try again!"
    })
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    age = forms.CharField(max_length=10, error_messages={
        'required': "Please provide an age for the team!"
    })
    gender = forms.ChoiceField(choices=GENDER_CHOICES, error_messages={
        'required': "Please choose a gender for the team!"
    })

    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ['password']
        error_messages = {
            'username': {
                'required': "Please give a team name!",
                'max_length': "This team name is too long! Try again!",
                'unique': "A team with name already exists! Try again!"
            },
            'email': {
                'invalid': "This email is invalid! Try again!"
            }
        }

    def __init__(self, *args, **kwargs):
        super(CreateTeamForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and hasattr(kwargs['instance'], 'profile'):
            self.fields['description'].initial = kwargs['instance'].profile.description
            self.fields['age'].initial = kwargs['instance'].profile.age
            self.fields['gender'].initial = kwargs['instance'].profile.gender

    # If we're saving a new team
    def saveNew(self):
        team = super(CreateTeamForm, self).save(commit=False)

        if self.cleaned_data.get('password'):
            random_pass = self.cleaned_data.get('password')
            is_random = False
        else:
            random_pass = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))
            is_random = True

        team.set_password(random_pass)
        team.save()

        profile = TeamProfile(team=team, description=self.cleaned_data.get('description'), age=self.cleaned_data.get('age'), gender=self.cleaned_data.get('gender'))
        profile.save()

        team.change_group('Team')

        return dict(team=team, password=random_pass, random=is_random, profile=profile)

    # If we're editing an old team
    def saveEdit(self):
        team = super(CreateTeamForm, self).save(commit=False)

        if self.cleaned_data.get('password'):
            team.set_password(self.cleaned_data.get('password'))

        team.save()

        if hasattr(team, 'profile'):
            team.profile.description = self.cleaned_data.get('description')
            team.profile.age = self.cleaned_data.get('age')
            team.profile.gender = self.cleaned_data.get('gender')
            team.profile.save()
        else:
            profile = TeamProfile(team=team, description=self.cleaned_data.get('description'), age=self.cleaned_data.get('age'), gender=self.cleaned_data.get('gender'))
            profile.save()
