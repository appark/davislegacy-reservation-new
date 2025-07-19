from django.forms import ModelForm
from django import forms

from reservations.models import Field, TimeSlot

class FieldForm(ModelForm):
    class Meta:
        model = Field
        fields = ['name']
        error_messages = {
            'name': {
                'required': 'Please give a field name!',
                'max_length': 'This field name is too long. Try again!'
            }
        }

class TimeSlotForm(ModelForm):
    start_time = forms.TimeField(
        required=True,
        input_formats=['%H:%M:%S', '%H:%M:%S.%f', '%H:%M', '%I:%M %p', '%I:%M:%S %p']
    )
    end_time = forms.TimeField(
        required=True,
        input_formats=['%H:%M:%S', '%H:%M:%S.%f', '%H:%M', '%I:%M %p', '%I:%M:%S %p']
    )

    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']
        exclude = ['location']

    def clean(self):
        cleaned_data = super(TimeSlotForm, self).clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("The start time must be before the end time!")

            if self.instance.location:
                for timeslot in self.instance.location.timeslot_set.filter(active=True):
                    if timeslot.start_time < end_time and timeslot.end_time > start_time:
                        raise forms.ValidationError("The timeslot you have chosen intersects with an existing timeslot!")

        return cleaned_data

    def save(self, commit=True):
        timeslot = super(TimeSlotForm, self).save(commit=False)

        if commit:
            timeslot.save()

            # Add overlapping custom timeslots
            overlap = TimeSlot.objects.filter(active=False, location=timeslot.location, start_time__lt=timeslot.end_time, end_time__gt=timeslot.start_time)
            timeslot.overlap.add(*overlap)

        return timeslot
