from django.shortcuts import render, redirect
from django.http import HttpResponse
import unicodecsv as csv
from datetime import datetime
from django.contrib import messages

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from reservations.models import Reservation, Tournament
from reservations.utils import date_bounds, get_website_setting, is_superuser

def dashboard(request):
    # Break current reservations and tournaments up by gametype
    # Format: { gametype1: { 'reservations': [resv1, resv2, ...], 'tournaments': [tour1, tour2, ...] }, gametype2: { ... }, ... }
    reservations = Reservation.objects.filter(active=True, date__gte=date_bounds()['start'], approved=True).select_related('timeslot', 'location', 'team', 'team__profile', 'gametype')
    tournaments = Tournament.objects.filter(active=True).select_related('gametype').prefetch_related('locations')

    gametypes = {}
    other_tournaments = []
    for reservation in reservations:
        if reservation.gametype in gametypes:
            gametypes[reservation.gametype]['reservations'].append(reservation)
        else:
            gametypes[reservation.gametype] = { 'reservations': [reservation], 'tournaments': [] }
    for tournament in tournaments:
        # If this tournament doesn't have a gametype, put it aside
        if not tournament.gametype:
            other_tournaments.append(tournament)
            continue
        if tournament.gametype in gametypes:
            gametypes[tournament.gametype]['tournaments'].append(tournament)
        else:
            gametypes[tournament.gametype] = { 'reservations': [], 'tournaments': [tournament] }

    context = {
        'gametypes': gametypes,
        'other_tournaments': other_tournaments
    }

    if is_superuser(request.user):
        widgets_context = get_widgets_context()
        context.update(widgets_context)

        return render(request, 'reservations/general/widgets.html', context)
    else:
        return render(request, 'reservations/general/dashboard.html', context)

def get_widgets_context():
    # Recent Actiivty Widget
    raw_recent_activity = LogEntry.objects.all().order_by('-action_time').select_related('user')[:25]
    recent_activity = []
    for activity in raw_recent_activity:
        message = activity.change_message.split(":", 1)

        if len(message) != 2:
            continue

        recent_activity.append({ 'tag': message[0], 'message': message[1], 'user': activity.user.username, 'time': activity.action_time })

    # Teams Widget
    teams = User.objects.filter(is_active=True, groups__name='Team').order_by('username').select_related('profile').prefetch_related('groups')

    # Stats Widget
    bounds = date_bounds()
    reservations = Reservation.objects.filter(active=True, approved=True, date__range=[bounds['start'], bounds['end']]).select_related('location')
    tournaments = Tournament.objects.filter(active=True, start_date__lte=bounds['end'], end_date__gte=bounds['start']).prefetch_related('locations')

    reservations_count = reservations.count()
    tournaments_count = tournaments.count()

    # Pie Widget
    field_data = {}
    for reservation in reservations.iterator(chunk_size=2000):
        if reservation.location in field_data:
            field_data[reservation.location]['count'] += 1
            field_data[reservation.location]['resv_count'] += 1
        else:
            field_data[reservation.location] = { 'count': 1, 'resv_count': 1, 'tour_count': 0 }
    for tournament in tournaments.iterator(chunk_size=2000):
        for location in tournament.locations.filter(active=True):
            if location in field_data:
                field_data[location]['count'] += 1
                field_data[location]['tour_count'] += 1
            else:
                field_data[location] = { 'count': 1, 'resv_count': 0, 'tour_count': 1 }

    # Pending Widget
    pending = Reservation.objects.filter(active=True, approved=False).select_related('team', 'team__profile', 'location')[:10]

    context = {
        'recent_activity': recent_activity,
        'teams': teams,
        'reservations_count': reservations_count,
        'tournaments_count': tournaments_count,
        'field_data': field_data,
        'pending': pending
    }

    return context


def get_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="weekly_games.csv"'

    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%m/%d/%Y')
            end_date = datetime.strptime(request.GET.get('end_date'), '%m/%d/%Y')
            bounds = dict(start=start_date, end=end_date)
        except:
            messages.error(request, "The date range for the excel download was incorrectly formatted. Please try again!")
            return redirect('dashboard')
    else:
        bounds = date_bounds(start_bound=int(get_website_setting('CALENDAR_RANGE_START', 0)), end_bound=int(get_website_setting('CALENDAR_RANGE_END', 6)))

    reservations = Reservation.objects.filter(active=True, approved=True, date__range=[bounds['start'], bounds['end']]).select_related('timeslot', 'location', 'team', 'gametype')

    writer = csv.writer(response)
    writer.writerow(["GameNum", "GameDate", "GameTime", "GameAge", "GameLevel", "Gender", "Location", "HomeTeam", "AwayTeam", "GameDescription", "CrewSize", "CrewDescription", "Notes"])
    writer.writerow([""])

    if reservations:
        for reservation in reservations:
            writer.writerow([
                reservation.game_number,
                reservation.date.strftime('%m/%d/%Y'),
                reservation.timeslot.start_time.strftime('%I:%M %p'),
                reservation.age,
                reservation.gametype.type,
                # TODO: Make this a permanent fix by performing database migrations
                "Female" if reservation.gender == "girls" else "Male",
                reservation.location.name,
                reservation.team.fullname,
                reservation.game_opponent,
                "",
                "",
                "",
                ""
            ])
    else:
        writer.writerow(["There are no reservations."])

    tournaments = Tournament.objects.filter(active=True, start_date__lte=bounds['end'], end_date__gte=bounds['start']).select_related('gametype').prefetch_related('locations')

    if tournaments:
        writer.writerow([""])
        writer.writerow(["Tournament Name", "Fields", "Start Date", "End Date"])
        for tournament in tournaments:
            fields = ", ".join([str(x) for x in tournament.locations.filter(active=True)])

            if tournament.gametype:
                name = tournament.gametype.type + " " + tournament.name
            else:
                name = tournament.name

            writer.writerow([
                name,
                fields,
                tournament.start_date.strftime('%m/%d/%Y'),
                tournament.end_date.strftime('%m/%d/%Y')
            ])

    return response
