from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.urls import reverse
from django.contrib import messages
from django.utils.html import escape

from django.contrib.admin.models import DELETION, CHANGE

from reservations.decorators import can_edit_reservation
from reservations.utils import clear_tokens, log_message, has_reservation_block

from reservations.models import Reservation, Tournament

def four_oh_four(request):
    return render(request, 'reservations/general/404.html')

@login_required
def logout_user(request):
    clear_tokens(request)
    logout(request)
    return redirect('/')

    return render(request, 'registration/logged_out.html')

def reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if not reservation.active:
        return redirect('dashboard')

    return render(request, 'reservations/general/reservation.html', { 'reservation': reservation })

def tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    if not tournament.active:
        return redirect('dashboard')

    return render(request, 'reservations/general/tournament.html', { 'tournament': tournament })

@can_edit_reservation
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    log_message(request, reservation, DELETION, "Deleted Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))
    messages.success(request, "Deleted reservation <b>{}</b>!".format(escape(str(reservation))), extra_tags="undo={}".format(reverse('recovery_reservation', kwargs={ 'reservation_id': reservation.pk })))

    reservation.active = False
    reservation.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@can_edit_reservation
def recovery_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if (Reservation.objects.filter(active=True, date=reservation.date, timeslot=reservation.timeslot).count() > 1
        or Tournament.objects.filter(active=True, start_date__lte=reservation.date, end_date__gte=reservation.date, locations=reservation.location)):
        messages.error(request, "This reservation overlaps with another reservation/tournament! It can not be recovered.")
    else:
        reservation.active = True
        reservation.save()

        log_message(request, reservation, CHANGE, "Recovered Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))
        messages.success(request, "The reservation <b>{}</b> was recovered!".format(escape(str(reservation))))
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def new_reservation(request):
    clear_tokens(request)
    request.session['resv_tokentype'] = "new"
    request.session['resv_step'] = 1
    request.session['resv_next'] = request.GET.get("next", None)

    return redirect('editor_step1')

@can_edit_reservation
def edit_reservation(request, reservation_id):
    clear_tokens(request)

    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if has_reservation_block(request, reservation.date):
        messages.error(request, "You cannot modify this reservation, because today's date is too close to the reservation's date.")
        return redirect('dashboard')

    request.session['resv_tokentype'] = "edit"
    request.session['resv_id'] = reservation.pk
    request.session['resv_step'] = 1
    request.session['resv_next'] = request.GET.get("next", None)

    request.session['resv_game_number'] = reservation.game_number
    request.session['resv_game_opponent'] = reservation.game_opponent
    request.session['resv_date'] = reservation.date.strftime("%m/%d/%Y")
    request.session['resv_team'] = reservation.team.pk
    request.session['resv_location'] = reservation.location.pk
    request.session['resv_gametype'] = reservation.gametype.pk
    request.session['resv_timeslot'] = reservation.timeslot.pk

    return redirect('editor_step1')
