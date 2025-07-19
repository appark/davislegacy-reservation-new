from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, DELETION, CHANGE

from reservations.models import Tournament
from reservations.forms import TournamentsForm
from reservations.utils import message_errors, clear_tokens, send_email_superusers, clean_tournaments, log_message
from reservations.decorators import superuser_required, token_required

@superuser_required
def all_tournaments(request):

    form = TournamentsForm()
    tournaments = Tournament.objects.filter(active=True).select_related('gametype').prefetch_related('locations')
    return render(request, 'reservations/admin/tournaments/all_tournaments.html', { 'tournaments': tournaments, 'form': form })

@superuser_required
@token_required(block_all=True)
def new_tournament(request):
    if request.method == 'POST':
        form = TournamentsForm(request.POST)

        if form.is_valid():
            tournament = form.save()
            log_message(request, tournament, ADDITION, "New Tournament: {}".format(tournament))
            send_email_superusers("New Tournament", 'reservations/email/new_tournament.html', { 'tournament': tournament })

            clear_tokens(request)

            messages.success(request, "Created new tournament <b>{}</b>!".format(escape(tournament.name)))
            return redirect('all_tournaments')
        else:
            message_errors(request, form.errors)
    else:
        form = TournamentsForm()
    return render(request, 'reservations/admin/tournaments/edit_tournament.html', { 'form': form })

@superuser_required
@token_required(block_all=True)
def edit_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    current_locations = tournament.locations.values_list('id', flat=True)

    if request.method == 'POST':
        form = TournamentsForm(request.POST, instance=tournament)

        if form.is_valid():
            tournament = form.save()
            log_message(request, tournament, CHANGE, "Modified Tournament: {}".format(tournament))

            clear_tokens(request)

            messages.success(request, "Modified tournament <b>{}</b>!".format(escape(tournament.name)))
            return redirect('all_tournaments')
        else:
            message_errors(request, form.errors)
    else:
        form = TournamentsForm(instance=tournament)
    return render(request, 'reservations/admin/tournaments/edit_tournament.html', { 'form': form, 'tournament': tournament, 'current_locations': current_locations })

@superuser_required
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    log_message(request, tournament, DELETION, "Deleted Tournament: {}".format(tournament))
    tournament.active = False
    tournament.save()

    messages.success(request, "Deleted tournament <b>{}</b>!".format(escape(tournament.name)), extra_tags="undo={}".format(reverse('recovery_tournament', kwargs={ 'tournament_id': tournament.pk })))
    return redirect('all_tournaments')
