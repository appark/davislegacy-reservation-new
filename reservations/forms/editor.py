from django import forms
from django.shortcuts import get_object_or_404

from reservations.utils import get_object_or_none
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

from django.contrib.auth.models import User
from reservations.models import Reservation, GameType, TimeSlot, Field, Tournament
from reservations.utils import is_superuser, is_manager

class EditorStep1Form(forms.Form):
    game_number = forms.IntegerField(error_messages={
        'required': "Please give a game number!",
        'invalid': "The game number must be a number!"
    })
    game_opponent = forms.CharField(max_length=2048, error_messages={
        'required': "Please give a game opponent!",
        'max_length': "The game opponent's name is too long. Try again!"
    })
    gametype = forms.ModelChoiceField(queryset=GameType.objects.none(), error_messages={
        'required': "Please select a valid gametype!"
    })
    team = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    date = forms.DateField(error_messages={
        'required': "Please give a date!",
        'invalid': "The date given was invalid. Try again!"
    })

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditorStep1Form, self).__init__(*args, **kwargs)

        if self.user and not is_manager(self.user):
            self.fields['team'].initial = self.user

    def populate_form(self, request):
        self.fields['game_number'].initial = request.session.get('resv_game_number', None)
        self.fields['game_opponent'].initial = request.session.get('resv_game_opponent', None)

        # Get the gametype if it was trashed
        if request.session.get('resv_gametype', None):
            self.fields['gametype'].queryset = GameType.objects.filter(Q(active=True) | Q(pk=request.session.get('resv_gametype')))
            self.fields['gametype'].initial = get_object_or_none(GameType, pk=request.session.get('resv_gametype', -1))
        else:
            self.fields['gametype'].queryset = GameType.objects.filter(active=True)

        # Populate team field
        resv_team = request.session.get('resv_team', None)

        if self.user:
            # If they are a manager, give them the choice of their teams.
            # If they are a team, just give them the option to choose only their team.
            if is_manager(self.user):
                # Get the team even if they were trashed
                if resv_team:
                    self.fields['team'].queryset = self.user.manager_profile.teams.filter(Q(is_active=True) | Q(pk=resv_team))
                else:
                    self.fields['team'].queryset = self.user.manager_profile.teams.filter(is_active=True)
            else:
                self.fields['team'].queryset = User.objects.filter(pk=self.user.pk)
        else:
            # Else, they are a superuser
            # Once again, get the team even if they were trashed. Should probably figure out a way to not repeat this code someday.
            if resv_team:
                self.fields['team'].queryset = User.objects.filter((Q(is_active=True) & Q(groups__name='Team')) | Q(pk=resv_team))
            else:
                self.fields['team'].queryset = User.objects.filter(is_active=True, groups__name='Team')

        if resv_team:
            self.fields['team'].initial = get_object_or_none(User, pk=resv_team)

        resv_date = request.session.get('resv_date', None)
        if resv_date:
            self.fields['date'].initial = datetime.strptime(resv_date, "%m/%d/%Y").date()

    def populate_session(self, request):
        request.session['resv_game_number'] = self.cleaned_data.get('game_number')
        request.session['resv_game_opponent'] = self.cleaned_data.get('game_opponent')
        request.session['resv_gametype'] = self.cleaned_data.get('gametype').pk
        request.session['resv_date'] = self.cleaned_data.get('date').strftime('%m/%d/%Y')
        request.session['resv_team'] = self.cleaned_data.get('team').pk
        if hasattr(self.cleaned_data.get('team'), 'profile'):
            request.session['resv_age'] = self.cleaned_data.get('team').profile.age
            request.session['resv_gender'] = self.cleaned_data.get('team').profile.gender

    def clean_team(self):
        form_team = self.cleaned_data['team']

        if self.user and not is_manager(self.user):
            form_team = self.user

        if not form_team:
            raise forms.ValidationError("Please select a valid team!")

        return form_team

    def clean_date(self):
        form_date = self.cleaned_data.get('date')
        today = timezone.localtime(timezone.now()).date()

        if form_date < today:
            raise forms.ValidationError("Please choose a date greater than or equal to today!")

        return form_date

class EditorStep2Form(forms.Form):
    timeslot = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=TimeSlot.objects.none(), required=False)

    # Whether they want a custom timeslot
    custom_timeslot = forms.BooleanField(required=False)
    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)
    field = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(EditorStep2Form, self).__init__(*args, **kwargs)
        self.fields['field'].choices = [('', '---------')] + Field.objects.natsorted(include={ 'active': True }, format='tuple')

    def populate_form(self, request):
        # Get the 'resv_date' from session.
        date = request.session.get('resv_date', None)
        if date:
            date = datetime.strptime(date, "%m/%d/%Y").date()
        else:
            return False

        # Get the 'resv_team' from session.
        team = get_object_or_none(User, pk=request.session.get('resv_team', -1))
        if not team:
            return False

        # Get timeslots that are not reserved for that date and that the team can reserve
        # And give that queryset to the form.
        # Also check if this is an edit. If so, get the existing reservation.

        # Get all reservations that occur on this date
        already_reserved = Reservation.objects.filter(active=True, date=date)

        # Get all tournaments that intersect with this date
        tournaments = Tournament.objects.filter(active=True, start_date__lte=date, end_date__gte=date)

        # Let them see the timeslot this reservation occupies
        resv_timeslot = get_object_or_none(TimeSlot, pk=request.session.get('resv_timeslot', -1))
        timeslot_pk = -1

        if resv_timeslot:
            resv_tokentype = request.session.get('resv_tokentype', None)

            # If this is an edit, check to make sure that this timeslot matches the date applied.
            if resv_tokentype == "edit":
                resv_reservation = get_object_or_none(Reservation, pk=request.session.get('resv_id', -1))

                if resv_reservation and date == resv_reservation.date:
                    timeslot_pk = resv_timeslot.pk
            else:
                timeslot_pk = resv_timeslot.pk

        if not is_superuser(request.user):
            # Get timeslots where the team is allowed to sign up, and exclude those that already have a reservation or a tournament going on.
            choices = TimeSlot.objects.filter(
                (
                    Q(active=True) &                                                 # It's an active timeslot
                    Q(location__in=team.field_set.filter(active=True)) &             # This team can use this timeslot's field
                    ~Q(reservation__in=already_reserved) &                           # This timeslot doesn't have a reservation yet
                    ~Q(overlap__reservation__in=already_reserved) &                  # This custom timeslot doesn't overlap with reservations
                    ~Q(location__tournament__in=tournaments)                         # Tournaments aren't taking place this day.
                ) | Q(pk=timeslot_pk)).distinct().order_by('location', 'start_time') # Or if this is the current timeslot.
        else:
            # They are a superuser, let them choose any timeslot.
            choices = TimeSlot.objects.filter(
                (
                    Q(active=True) &
                    ~Q(reservation__in=already_reserved) &
                    ~Q(overlap__reservation__in=already_reserved) &
                    ~Q(location__tournament__in=tournaments)
                ) | Q(pk=timeslot_pk)).distinct().order_by('location', 'start_time')

        self.fields['timeslot'].queryset = choices

        # Generate a key/value dictionary for fields and timeslots.
        # Format: { field1: [timeslot1, timeslot2, ...], field2: [timeslot1, timeslot2, ...], ... }
        self.timeslot_choices = {}
        for timeslot in choices:
            if timeslot.location in self.timeslot_choices:
                self.timeslot_choices[timeslot.location].append(timeslot)
            else:
                self.timeslot_choices[timeslot.location] = [timeslot]
        for field in self.timeslot_choices.keys():
            if len(self.timeslot_choices[field]) == 0:
                del self.timeslot_choices[field]

        # Restore initial values for timeslots, if they go back.
        self.fields['timeslot'].initial = resv_timeslot

        return True

    # Clean all fields
    def clean(self):
        cleaned_data = super(EditorStep2Form, self).clean()
        if cleaned_data.get('custom_timeslot'):
            if not all([cleaned_data.get('field'), cleaned_data.get('start_time'), cleaned_data.get('end_time')]):
                raise forms.ValidationError("Please fill out all fields for the custom timeslot!")

            self.field = cleaned_data.get('field')
            self.start_time = cleaned_data.get('start_time')
            self.end_time = cleaned_data.get('end_time')

            if self.start_time >= self.end_time:
                raise forms.ValidationError("The start time must be before the end time!")
                return
        elif not cleaned_data.get('timeslot'):
            raise forms.ValidationError("Please choose a timeslot!")
            return

    def populate_session(self, request):
        if self.cleaned_data.get('custom_timeslot'):
            if not is_superuser(request.user):
                return False

            field = get_object_or_404(Field, pk=self.field)
            timeslot = TimeSlot(active=False, start_time=self.start_time, end_time=self.end_time, location=field)
            timeslot.save()

            # Add overlapping active timeslots
            overlap = TimeSlot.objects.filter(active=True, location=timeslot.location, start_time__lt=timeslot.end_time, end_time__gt=timeslot.start_time)
            timeslot.overlap.add(*overlap)

            request.session['resv_timeslot'] = timeslot.pk
            request.session['resv_location'] = field.pk
        else:
            request.session['resv_timeslot'] = self.cleaned_data.get('timeslot').pk
            request.session['resv_location'] = self.cleaned_data.get('timeslot').location.pk

        return True
