from django.forms import ModelForm
from django import forms
from django.db.models import Q
from reservations.models import Tournament, Field, GameType

class TournamentsForm(ModelForm):
    start_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
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
