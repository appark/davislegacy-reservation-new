from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Prefetch
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, DELETION, CHANGE

from reservations.utils import message_errors, send_email, send_email_superusers, log_message
from reservations.decorators import superuser_required

from django.contrib.auth.models import User
from reservations.models import Field
from reservations.forms import CreateTeamForm
from reservations.api.forms import APITeamModifyFieldsForm

@superuser_required
def all_teams(request):
    temp_teams = User.objects.filter(is_active=True, groups__name='Team').order_by('username').select_related('profile').prefetch_related(Prefetch('field_set', queryset=Field.objects.filter(active=True), to_attr='fields'))
    teams = []

    form = APITeamModifyFieldsForm()

    for team in temp_teams:
        teams.append({
            'team': team,
            'fields': [field.pk for field in team.fields]
        })

    return render(request, 'reservations/admin/teams/all_teams.html', { 'teams': teams, 'form': form })

@superuser_required
def delete_team(request, team_id):
    team = get_object_or_404(User, pk=team_id)

    team.is_active = False
    team.save()

    log_message(request, team, DELETION, "Deleted Team: {}".format(team.username))
    messages.success(request, "Deleted team <b>{}</b>!".format(escape(team.username)), extra_tags="undo={}".format(reverse('recovery_team', kwargs={ 'team_id': team.pk })))

    return redirect('all_teams')

@superuser_required
def new_team(request):
    if request.method == 'POST':
        form = CreateTeamForm(request.POST)

        if form.is_valid():
            teamDict = form.saveNew()

            if teamDict['team'].email:
                send_email("New Team: {}".format(teamDict['team'].username), 'reservations/email/new_team.html', { 'team': teamDict['team'], 'password': teamDict['password'], 'link': reverse('login') }, [teamDict['team'].email])

            log_message(request, teamDict['team'], ADDITION, "New Team: {}".format(teamDict['team'].username))
            send_email_superusers("New Team: {}".format(teamDict['team'].username), 'reservations/email/new_team_done.html', { 'team': teamDict['team'] })
            return render(request, 'reservations/admin/teams/new_team_done.html', { 'team': teamDict['team'], 'password': teamDict['password'], 'random': teamDict['random'], 'profile': teamDict['profile'] })
        else:
            message_errors(request, form.errors)
    else:
        form = CreateTeamForm()
    return render(request, 'reservations/admin/teams/edit_team.html', { 'form': form })

@superuser_required
def edit_team(request, team_id):
    team = get_object_or_404(User, pk=team_id)
    if request.method == 'POST':
        form = CreateTeamForm(request.POST, instance=team)

        if form.is_valid():
            form.saveEdit()

            log_message(request, team, CHANGE, "Modified Team: {}".format(team.username))
            messages.success(request, "Modified Team <b>{}</b>!".format(escape(team.username)))
            return redirect('all_teams')
        else:
            message_errors(request, form.errors)
    else:
        form = CreateTeamForm(instance=team)

    return render(request, 'reservations/admin/teams/edit_team.html', { 'form': form, 'team': team })
