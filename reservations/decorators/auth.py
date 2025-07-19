from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Q
from rest_framework.permissions import BasePermission
import time

from reservations.models import ReservationToken
from reservations.utils import get_website_setting, is_superuser, is_manager, is_editor

""" Auth Decorators """
# Decorates the login against the given tester function
def login_decorator(view, tester_func, error_msg):
    def decorator(request, *args, **kwargs):
        if request.user.is_authenticated:
            if tester_func(request.user, *args, **kwargs):
                return view(request, *args, **kwargs)
            messages.error(request, error_msg)
            return redirect('dashboard')
        else:
            return redirect(reverse('login') + "?next=" + request.path)
    return decorator

# Checks whether this person is a superuser.
def superuser_required(view):
    return login_decorator(view, is_superuser, "Sorry! This page is meant for superusers only.")

# Checks whether this person is a manager.
def manager_required(view):
    return login_decorator(view, is_manager, "Sorry! This page is meant for team managers only.")

# Checks whether a team has permission to edit/delete this reservation.
def can_edit_reservation(view):
    return login_decorator(view, is_editor, "Sorry! You don't have permission to visit this page.")

# Rest API permissions to check whether they are a superuser
class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return is_superuser(request.user)

""" Token Decorator """
# Determines whether the person has a session token for reservations yet.
def token_required(block_all=False, timeout_msg=False):
    def wrapper(view):
        def decorator(request, *args, **kwargs):
            # Clean out any outdated tokens.
            timeout = int(get_website_setting('RESERVATION_TOKEN_TIMEOUT', 10))
            ReservationToken.objects.filter(issued__lt=(timezone.now() - timedelta(minutes=timeout))).delete()

            if not block_all:
                # Obtain reservation date.
                resv_date = request.session.get('resv_date', None)
                if resv_date:
                    resv_date = datetime.strptime(resv_date, "%m/%d/%Y").date()
                else:
                    messages.warning(request, "We couldn't obtain a session token! Refresh the page and try again.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))

                # Check whether this person has a token for this date.
                if ReservationToken.objects.filter(team=request.user, hold_date=resv_date).count() == 1:
                    return view(request, *args, **kwargs)

                # If they don't have a token, try to get one.
                # Check for open tokens on this date, or block all tokens.
                open_token = ReservationToken.objects.filter(Q(hold_date=resv_date) | Q(hold_date=None)).first()
                if not open_token:
                    token = ReservationToken(team=request.user, hold_date=resv_date)
                    token.save()
                    return view(request, *args, **kwargs)
            else:
                # Check whether this person has a block all reservation token (hold_date is blank)
                if ReservationToken.objects.filter(team=request.user, hold_date=None).count() == 1:
                    return view(request, *args, **kwargs)

                # If they don't have a token, try to get one.
                # Check if there are any tokens out.
                open_token = ReservationToken.objects.all().first()
                if not open_token:
                    token = ReservationToken(team=request.user, hold_date=None)
                    token.save()
                    return view(request, *args, **kwargs)


            # We failed to get a token, so display an error.
            # Gets the minutes left by first converting to unix timestamps, subtracting, then dividing by 60
            minutes_left = timeout - int((time.mktime(timezone.now().timetuple()) - time.mktime(open_token.issued.timetuple())) / 60)

            if timeout_msg:
                messages.warning(request, "Your session token timed out, and <b>{}</b> is currently making a reservation! Try again in <b>{}</b> minute(s).".format(open_token.team.fullname, minutes_left))
                return redirect('dashboard')
            else:
                messages.warning(request, "<b>{}</b> is currently making a reservation! Try again in <b>{}</b> minute(s).".format(open_token.team.fullname, minutes_left))
                return redirect(request.META.get('HTTP_REFERER', '/'))
        return decorator
    return wrapper
