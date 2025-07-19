from django.forms import ModelForm
from django import forms
from django.db.models import Q

from reservations.models import Tournament, Field, GameType

class TournamentsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TournamentsForm, self).__init__(*args, **kwargs)

        # Make sure they can see fields that have been trashed, if this is an edit
        if self.instance.pk:
            locations = Field.objects.natsorted(q_objects=(Q(active=True) | Q(tournament=self.instance)), format='q_tuple')
        else:
            locations = Field.objects.natsorted(include={ 'active': True }, format='tuple')

        self.fields['locations'] = forms.MultipleChoiceField(choices=locations, error_messages={
            'required': "Please choose a field name!"
        })

        # Make sure they can see gametypes that have been trashed, if this is an edit
        if self.instance.pk and self.instance.gametype:
            self.fields['gametype'].queryset = GameType.objects.filter(Q(active=True) | Q(pk=self.instance.gametype.pk))
        else:
            self.fields['gametype'].queryset = GameType.objects.filter(active=True)

        # Remove validators that cause date validation issues
        self.fields['start_date'].validators = []
        self.fields['end_date'].validators = []

    class Meta:
        model = Tournament
        fields = ['name', 'locations', 'gametype', 'start_date', 'end_date']

        error_messages = {
            'name': {
                'required': "Please give a tournament name!"
            },
            'start_date': {
                'required': "Please give a start date!"
            },
            'end_date': {
                'required': "Please give a end date!"
            }
        }

    def clean(self):
        cleaned_data = super(TournamentsForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("The start date must be before or equal to the end date!")
            
        return cleaned_data
