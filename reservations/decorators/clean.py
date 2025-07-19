from datetime import datetime
from django.db import transaction

from django.contrib.auth.models import User

from reservations.models import Reservation, ArchivedReservation, Field, TimeSlot, GameType, Tournament, ArchivedTournament
from reservations.utils import get_website_setting, set_website_setting, date_bounds

# Cleans up the database
# Archives old reservations and cleans out inactive and/or
# out-of-date reservations, gametypes, fields, and timeslots
def clean_task(view):
    def clean_reservations():
        reservations = Reservation.objects.filter(date__lt=date_bounds()['start'])
        for reservation in reservations.iterator():
            context = {
                'game_number': reservation.game_number,
                'game_opponent': reservation.game_opponent,
                'date': reservation.date,
                'approved': reservation.approved,
                'team': reservation.team.fullname,
                'location': reservation.location.name,
                'gametype': reservation.gametype.type,
                'start_time': reservation.timeslot.start_time,
                'end_time': reservation.timeslot.end_time,
                'deleted': not reservation.active,
                'age': reservation.age,
                'gender': reservation.gender,
            }
            archive = ArchivedReservation(**context)
            archive.save()

        reservations.delete()

    def clean_tournaments():
        tournaments = Tournament.objects.filter(active=False)

        for tournament in tournaments.iterator():
            context = {
                'name': tournament.name,
                'start_date': tournament.start_date,
                'end_date': tournament.end_date,
                'gametype': tournament.gametype.type if tournament.gametype else "",
                'locations': ",".join([x.name for x in tournament.locations.all()])
            }
            archive = ArchivedTournament(**context)
            archive.save()

        tournaments.delete()

    def clean_gametypes():
        gametypes = GameType.objects.filter(active=False)
        for gametype in gametypes.iterator():
            if gametype.reservation_set.all().count() == 0 and gametype.tournament_set.all().count() == 0:
                gametype.delete()

    def clean_timeslots():
        timeslots = TimeSlot.objects.filter(active=False)
        for timeslot in timeslots.iterator():
            if timeslot.reservation_set.all().count() == 0:
                timeslot.delete()

    def clean_fields():
        fields = Field.objects.filter(active=False)
        for field in fields.iterator():
            if field.reservation_set.all().count() == 0 and field.tournament_set.all().count() == 0:
                field.delete()

    def clean_teams():
        teams = User.objects.filter(is_active=False)
        for team in teams.iterator():
            if team.reservation_set.all().count() == 0:
                team.delete()

    def decorator(request, *args, **kwargs):
        clean_date = date_bounds()['start']
        last_clean_date = datetime.strptime(get_website_setting('LAST_CLEAN_DATE', '01/01/2016'), '%m/%d/%Y').date()

        if(clean_date > last_clean_date):
            with transaction.atomic():
                clean_reservations()
                clean_tournaments()
                clean_gametypes()
                clean_timeslots()
                clean_fields()
                clean_teams()

                set_website_setting('LAST_CLEAN_DATE', clean_date.strftime('%m/%d/%Y'))

        return view(request, *args, **kwargs)
    return decorator
