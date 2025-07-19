from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.utils.html import escape

from django.contrib.admin.models import CHANGE

from django.contrib.auth.models import User
from reservations.models import Reservation, Field, Tournament, GameType
from reservations.decorators import superuser_required, clean_task, token_required
from reservations.utils import send_email_superusers, log_message, message_errors, clear_tokens
from reservations.forms import SwapForm

@superuser_required
@clean_task
def all_reservations(request):
    pending = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), approved=False).select_related('timeslot', 'location', 'team', 'team__profile', 'gametype')
    reservations = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), approved=True).select_related('timeslot', 'location', 'team', 'team__profile', 'gametype')
    return render(request, 'reservations/admin/all_reservations.html', { 'pending': pending, 'reservations': reservations })

@superuser_required
def approve_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    reservation.approved = not reservation.approved
    reservation.save()

    if reservation.approved:
        log_message(request, reservation, CHANGE, "Approved Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))
        send_email_superusers("Approved Reservation: {}".format(reservation), 'reservations/email/approve_reservation_done.html', { 'reservation': reservation, 'link': reverse('my_reservations') }, [reservation.team.email])
        messages.success(request, "The reservation <b>{}</b> was approved!".format(escape(str(reservation))))
    else:
        log_message(request, reservation, CHANGE, "Unapproved Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))
        messages.success(request, "The reservation <b>{}</b> was unapproved!".format(escape(str(reservation))))

    return redirect(request.META.get('HTTP_REFERER', '/'))

@superuser_required
def old_reservations(request):
    today = timezone.localtime(timezone.now()).date()

    reservations = Reservation.objects.filter(date__lt=today)
    return render(request, 'reservations/admin/old_reservations.html', { 'reservations': reservations })

@superuser_required
@token_required(block_all=True)
@transaction.atomic
def swap_reservations(request):
    ids = request.GET.get('ids', '').split(',')

    # Resolve ids to actual reservations
    reservations = Reservation.objects.filter(pk__in=ids).select_related('timeslot', 'team', 'location')

    # Check if we have the correct number of swappables
    if reservations.count() < 2:
        messages.error(request, "You must select 2+ reservations to swap. Try again!")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = SwapForm(request.POST, reservations=reservations)
        if form.is_valid():
            swapped_reservations = form.save()

            clear_tokens(request)

            for reservation in swapped_reservations:
                log_message(request, reservation, CHANGE, "Swapped Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))

            messages.success(request, "Successfully swapped reservations!")
            return redirect('all_reservations')
        else:
            message_errors(request, form.errors)
    else:
        form = SwapForm(reservations=reservations)

    return render(request, 'reservations/admin/swap.html', { 'form': form, 'reservations': reservations })

@superuser_required
def recovery(request, field_id=None, tournament_id=None, gametype_id=None, team_id=None):
    # Attempt Recovery
    if field_id:
        field = get_object_or_404(Field, pk=field_id)
        field.active = True
        field.save()

        timeslots = field.timeslot_set.filter(active=False)
        for timeslot in timeslots:
            timeslot.active = True
            timeslot.save()

        log_message(request, field, CHANGE, "Recovered Field: {}".format(field.name))
        messages.success(request, "The field <b>{}</b> was recovered!".format(escape(field.name)))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    elif tournament_id:
        tournament = get_object_or_404(Tournament, pk=tournament_id)
        tournament.active = True
        tournament.save()

        log_message(request, tournament, CHANGE, "Recovered Tournament: {}".format(tournament))
        messages.success(request, "The tournament <b>{}</b> was recovered!".format(escape(tournament.name)))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    elif gametype_id:
        gametype = get_object_or_404(GameType, pk=gametype_id)
        gametype.active = True
        gametype.save()

        log_message(request, gametype, CHANGE, "Recovered Gametype: {}".format(gametype.type))
        messages.success(request, "The gametype <b>{}</b> was recovered!".format(escape(gametype.type)))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    elif team_id:
        team = get_object_or_404(User, pk=team_id)
        team.is_active = True
        team.save()

        log_message(request, team, CHANGE, "Recovered Team: {}".format(team.username))
        messages.success(request, "Team <b>{}</b> was recovered!".format(escape(team.username)))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    today = timezone.localtime(timezone.now()).date()

    reservations = Reservation.objects.filter(active=False, date__gte=today).select_related('timeslot', 'location', 'team', 'gametype')
    fields = Field.objects.filter(active=False)
    tournaments = Tournament.objects.filter(active=False)
    gametypes = GameType.objects.filter(active=False)
    teams = User.objects.filter(is_active=False)

    return render(request, 'reservations/admin/recovery.html', { 'reservations': reservations, 'fields': fields, 'tournaments': tournaments, 'gametypes': gametypes, 'teams': teams })
