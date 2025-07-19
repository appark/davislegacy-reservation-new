# Misc. Utilities For All
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.utils import timezone
from datetime import datetime as dt
import datetime
import time
import pytz

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from django.contrib.admin.models import LogEntry
from dateutil.relativedelta import *

from django.contrib.auth.models import User
from reservations.models import Reservation, ReservationToken, Tournament, WebsiteSetting

""" Misc. Helper Functions """
# Displays all form errors
def message_errors(request, errors):
    for field in errors:
        for error in errors[field]:
            messages.error(request, error)

# Gets the object or returns None
def get_object_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

""" Cleaner Functions """
# Clears session tokens and reservation tokens
def clear_tokens(request):
    if not request.user.is_authenticated:
        return

    request.session.pop('resv_tokentype', None)
    request.session.pop('resv_id', None)
    request.session.pop('resv_step', None)

    request.session.pop('resv_game_number', None)
    request.session.pop('resv_game_opponent', None)
    request.session.pop('resv_date', None)
    request.session.pop('resv_team', None)
    request.session.pop('resv_location', None)
    request.session.pop('resv_gametype', None)
    request.session.pop('resv_timeslot', None)

    ReservationToken.objects.filter(team=request.user).delete()

# Cleans out old tournaments
def clean_tournaments():
    tournaments = Tournament.objects.filter(end_date__lt=date_bounds()['start'])

    for tournament in tournaments:
        tournament.delete()

""" Email Functions """
# Sends an email
def send_email(title, template, context, to_emails):
    send_mail(settings.EMAIL_SUBJECT_PREFIX + title, get_template(template).render(context), settings.SERVER_EMAIL, to_emails, fail_silently=True)

# Sends an email to superusers and optional others
def send_email_superusers(title, template, context, to_emails=[]):
    emails = []
    users = User.objects.filter(groups__name='Superuser')

    for user in users:
        if user.email and not user.email in to_emails:
            emails.append(user.email)
        if not user:
            continue

    all_emails = emails + to_emails

    send_email(title, template, context, all_emails)

""" Date Calculation Functions """
# Defines the date bounds of this week (The week starts on Sunday)
# The default start bound is this last Saturday (-1)
def date_bounds(start_bound=-1, end_bound=6):
    today = timezone.localtime(timezone.now()).date()
    weekday_start = today - datetime.timedelta(days=(today.weekday() + 1) % 7)

    start = weekday_start + datetime.timedelta(days=start_bound)
    end = start + datetime.timedelta(days=(end_bound - start_bound))

    return dict(start=start, end=end)

# Checks and makes sure that for a specific date, there are no blocks for editing reservations
def has_reservation_block(request, resv_date):
    # Always block non-authenticated users, if it gets here somehow
    if not request.user.is_authenticated:
        return True

    # Always say no blocks for superusers
    if is_superuser(request.user):
        return False

    today = timezone.localtime(timezone.now())
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Compute the block of time where editing this is invalid
    days_delta = int(get_website_setting('BLOCK_START_DAY', 0))
    time_delta = time.strptime(get_website_setting('BLOCK_START_TIME', "08:00:00"), "%H:%M:%S")

    # Get monday of this week
    this_monday = today + relativedelta(weekday=MO(-1))
    block_start = this_monday + relativedelta(days=days_delta, hours=time_delta.tm_hour, minutes=time_delta.tm_min, seconds=time_delta.tm_sec)

    # Get next monday, and next-next monday that is not today
    next_monday = today + relativedelta(days=+1, weekday=MO(+1))
    next_next_monday = today + relativedelta(days=+1, weekday=MO(+2))

    resv_date = datetime.datetime(year=resv_date.year, month=resv_date.month, day=resv_date.day)

    today = today.replace(tzinfo=pytz.utc)
    resv_date = resv_date.replace(tzinfo=pytz.utc)
    block_start = block_start.replace(tzinfo=pytz.utc)
    next_monday = next_monday.replace(tzinfo=pytz.utc)
    next_next_monday = next_next_monday.replace(tzinfo=pytz.utc)

    # If the reservation date is less than next monday, reject them
    if resv_date < next_monday and today >= block_start:
        return True

    # If the reservation date is less than next-next monday,
    # and today's date is greater than block_start, reject them
    #if resv_date < next_next_monday and today >= block_start:
    #    return True

    return False

""" Website Settings """
# Gets the desired website setting's value
# Returns the default (None) if it does not exist.
def get_website_setting(key, default=None):
    setting = get_object_or_none(WebsiteSetting, key=key)
    if setting:
        return setting.value
    else:
        return default

# Sets the desired website setting
# Returns True if successful
def set_website_setting(key, value):
    setting = get_object_or_none(WebsiteSetting, key=key)
    if setting:
        setting.value = str(value)
        setting.save()
        return True
    return False

""" Auth Functions """
# Returns whether this user is in a group
def in_group(user, group):
    if user:
        return user.groups.filter(name__in=[group]).exists()
    return False

# Returns whether this user is a Superuser
def is_superuser(user, *args, **kwargs):
    return user.is_superuser

# Returns whether this user is a Manager
def is_manager(user, *args, **kwargs):
    return in_group(user, 'Manager')

def is_editor(user, *args, **kwargs):
    if user:
        reservation = get_object_or_404(Reservation, pk=kwargs.get('reservation_id', -1))

        can_manage = False
        if hasattr(user, 'manager_profile'):
            can_manage = reservation.team in user.manager_profile.teams.all()

        return (reservation.team == user or can_manage or is_superuser(user))
    return False

""" Log Functions """
# Log message to the admin log
def log_message(request, obj, action_flag, change_message):
    LogEntry.objects.log_action(user_id=request.user.pk, content_type_id=ContentType.objects.get_for_model(obj).pk, object_id=obj.pk, object_repr=force_str(obj), action_flag=action_flag, change_message=change_message)
