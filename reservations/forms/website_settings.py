from django import forms
from datetime import datetime
from reservations.utils import set_website_setting, get_website_setting

class CalendarRangeForm(forms.Form):
    DAYS = ((-1, 'Saturday'), (0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'),
            (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday'))

    start_day = forms.ChoiceField(choices=DAYS)
    end_day = forms.ChoiceField(choices=DAYS)

    def __init__(self, *args, **kwargs):
        super(CalendarRangeForm, self).__init__(*args, **kwargs)
        self.fields['start_day'].initial = int(get_website_setting('CALENDAR_RANGE_START', -1))
        self.fields['end_day'].initial = int(get_website_setting('CALENDAR_RANGE_END', 5))

    @property
    def get_start_day(self):
        return dict(self.DAYS)[self.fields['start_day'].initial]

    @property
    def get_end_day(self):
        return dict(self.DAYS)[self.fields['end_day'].initial]

    def clean(self):
        cleaned_data = super(CalendarRangeForm, self).clean()
        if cleaned_data.get('start_day') > cleaned_data.get('end_day'):
            raise forms.ValidationError("The start day must be before the end day!")

    def save(self):
        set_website_setting('CALENDAR_RANGE_START', self.cleaned_data.get('start_day'))
        set_website_setting('CALENDAR_RANGE_END', self.cleaned_data.get('end_day'))

class TimeoutForm(forms.Form):
    time = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(TimeoutForm, self).__init__(*args, **kwargs)
        self.fields['time'].initial = int(get_website_setting('RESERVATION_TOKEN_TIMEOUT', 10))

    @property
    def get_time(self):
        return self.fields['time'].initial

    def clean_time(self):
        data = self.cleaned_data.get('time')
        if data < 0:
            raise forms.ValidationError("The timeout must be a positive number!")
        return data

    def save(self):
        set_website_setting('RESERVATION_TOKEN_TIMEOUT', self.cleaned_data.get('time'))

class BlockForm(forms.Form):
    DAYS = ((0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
            (3, 'Thursday'), (4, 'Friday'))

    start_day = forms.ChoiceField(choices=DAYS)
    start_time = forms.TimeField(input_formats=["%I:%M %p"])

    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        self.fields['start_day'].initial = int(get_website_setting('BLOCK_START_DAY', 0))
        time_str = get_website_setting('BLOCK_START_TIME', "00:00:00")

        try:
            parsed_time = datetime.strptime(time_str, "%H:%M:%S")
        except ValueError:
            parsed_time = datetime.strptime("00:00:00", "%H:%M:%S")

        self.fields['start_time'].initial = parsed_time.strftime("%I:%M %p")

    @property
    def get_start_day(self):
        return dict(self.DAYS)[self.fields['start_day'].initial]

    @property
    def get_start_time(self):
        return self.fields['start_time'].initial

    def save(self):
        set_website_setting('BLOCK_START_DAY', self.cleaned_data.get('start_day'))
        set_website_setting('BLOCK_START_TIME', self.cleaned_data.get('start_time').strftime("%H:%M:%S"))

class SiteConfigForm(forms.Form):
    site_name = forms.CharField(max_length=255, required=True, error_messages={
        'required': "Please provide a site name!",
        'max_length': "The site name is too long!"
    })

    def __init__(self, *args, **kwargs):
        super(SiteConfigForm, self).__init__(*args, **kwargs)
        self.fields['site_name'].initial = get_website_setting('SITE_NAME', '')

    @property
    def get_site_name(self):
        return self.fields['site_name'].initial

    def save(self):
        set_website_setting('SITE_NAME', self.cleaned_data.get('site_name'))

