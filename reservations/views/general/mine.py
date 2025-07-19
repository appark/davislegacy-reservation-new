from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from reservations.models import Reservation
from reservations.utils import is_manager

@login_required
def my_reservations(request):
    if is_manager(request.user):
        reservations = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), team__in=request.user.manager_profile.teams.all()).select_related('timeslot', 'location', 'team', 'gametype')
        return render(request, 'reservations/general/manager_reservations.html', { 'reservations': reservations })
    else:
        reservations = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), team=request.user).select_related('timeslot', 'location', 'team', 'gametype')
        return render(request, 'reservations/general/my_reservations.html', { 'reservations': reservations })
