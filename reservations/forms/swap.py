from django import forms

from reservations.models import Reservation

class SwapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        reservations = kwargs.pop('reservations')
        super(SwapForm, self).__init__(*args, **kwargs)

        # Generate Fields
        # In this case, initial is the original reservation,
        # and the thing they select is the one that we'll swap with.
        for reservation in reservations:
            self.fields['swap-with-{}'.format(reservation.pk)] = forms.ModelChoiceField(queryset=reservations)
            self.fields['swap-with-{}'.format(reservation.pk)].initial = reservation

    def clean(self):
        cleaned_data = super(SwapForm, self).clean()

        # Check if there are any repeats in the fields
        # If so, reject it!
        matched = set()
        for field, reservation in cleaned_data.items():
            if field.startswith('swap-with-'):
                if reservation.pk not in matched:
                    matched.add(reservation.pk)
                else:
                    raise forms.ValidationError("You gave two (or more) reservations the same timeslot. Try again!")

    def save(self):
        # Swap! We're taking advantage of the fact that we've got two different objects
        # that point to the same thing.
        swapped_reservations = []

        for field, reservation in self.cleaned_data.items():
            if field.startswith('swap-with-'):
                original = self.fields[field].initial

                original.date = reservation.date
                original.timeslot = reservation.timeslot

                original.save()
                swapped_reservations.append(original)

        return swapped_reservations
