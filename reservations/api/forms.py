from django import forms

from django.contrib.auth.models import User
from reservations.models import Field

class APIManagerIDForm(forms.Form):
    manager = forms.ModelChoiceField(widget=forms.HiddenInput(),
        queryset=User.objects.filter(is_active=True, groups__name='Manager'),
        error_messages={
            'invalid_choice': "This manager does not exist!"
        })

class APITeamIDForm(forms.Form):
    team = forms.ModelChoiceField(widget=forms.HiddenInput(),
        queryset=User.objects.filter(is_active=True, groups__name='Team'),
        error_messages={
            'invalid_choice': "This team does not exist!"
        })

class APIFieldIDForm(forms.Form):
    field = forms.ModelChoiceField(widget=forms.HiddenInput(),
        queryset=Field.objects.filter(active=True),
        error_messages={
            'invalid_choice': "This team does not exist!"
        })

class APITeamModifyFieldsForm(APITeamIDForm):
    def __init__(self, *args, **kwargs):
        super(APITeamModifyFieldsForm, self).__init__(*args, **kwargs)

        fields = Field.objects.natsorted(format='tuple', include={ 'active': True })
        self.fields['fields'] = forms.MultipleChoiceField(choices=fields, required=False)

    def save(self):
        if self.cleaned_data.get('fields'):
            self.cleaned_data.get('team').field_set.set(self.cleaned_data.get('fields'))
        else:
            self.cleaned_data.get('team').field_set.clear()

class APIFieldModifyTeamsForm(APIFieldIDForm):
    teams = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_active=True, groups__name='Team'), required=False)

    def save(self):
        if self.cleaned_data.get('teams'):
            self.cleaned_data.get('field').teams.set(self.cleaned_data.get('teams'))
        else:
            self.cleaned_data.get('field').teams.clear()

class APIGameTypeModifyTeamsForm(APIFieldIDForm):
    teams = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_active=True, groups__name='Team'), required=False)

    def save(self):
        if self.cleaned_data.get('teams'):
            self.cleaned_data.get('field').teams.set(self.cleaned_data.get('teams'))
        else:
            self.cleaned_data.get('field').teams.clear()

class APIManagerModifyTeamsForm(APIManagerIDForm):
    teams = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_active=True, groups__name='Team'), required=False)

    def save(self):
        if self.cleaned_data.get('teams'):
            self.cleaned_data.get('manager').manager_profile.teams.set(self.cleaned_data.get('teams'))
        else:
            self.cleaned_data.get('manager').manager_profile.teams.clear()
