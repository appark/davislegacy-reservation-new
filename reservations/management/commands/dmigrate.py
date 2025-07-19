from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import random, string
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from django.contrib.auth.models import User
from reservations.models import Field, TimeSlot, GameType, Reservation, TeamProfile, ArchivedReservation
from reservations.utils import date_bounds

# Database file to import
FILENAME = "/Users/JonathanYip/Documents/Git/DavisSoccer Extras/events.db"

# Initialize SQLAlchemy
engine = create_engine('sqlite:///' + FILENAME)
Base = declarative_base(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Classes for SQLAlchemy
class _Event(Base):
    __tablename__ = 'event_event'
    __table_args__ = { 'autoload': True }

class _Field(Base):
    __tablename__ = 'event_field'
    __table_args__ = { 'autoload': True }

class _FieldTime(Base):
    __tablename__ = 'event_fieldtime'
    __table_args__ = { 'autoload': True }

class _Gametype(Base):
    __tablename__ = 'event_gametype'
    __table_args__ = { 'autoload': True }

class _Team(Base):
    __tablename__ = 'event_team'
    __table_args__ = { 'autoload': True }

class _TeamField(Base):
    __tablename__ = 'event_teamfield'
    __table_args__ = { 'autoload': True }

class _User(Base):
    __tablename__ = 'auth_user'
    __table_args__ = { 'autoload': True }

class _Additional(Base):
    __tablename__ = 'event_additional'
    __table_args__ = { 'autoload': True }

def generateRandomPass():
    return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))

specialTeams = []
def getMatchingTeam(team_id):
    _team = session.query(_Team).get(team_id)
    if _team.id == 80:
        return specialTeams[0]
    elif _team.id == 78:
        return specialTeams[1]
    elif _team.id == 77:
        return specialTeams[2]
    elif _team.id == 76:
        return specialTeams[3]
    elif _team.id == 69:
        return specialTeams[4]
    elif _team.id == 68:
        return specialTeams[5]
    elif _team.id == 38:
        return specialTeams[6]
    else:
        username = session.query(_User).get(int(_team.user_id)).username
        return User.objects.get(username=username)

# Load gametypes
def loadGametypes():
    print("Loading Gametypes:")

    _gametypes = session.query(_Gametype).all()
    for _gametype in _gametypes:
        print("\t{}".format(_gametype.name))

        gametype = GameType(type=_gametype.name)
        gametype.save()

# Load teams
def loadTeams():
    print("Creating Special Teams...")

    specialTeams.append(User.objects.create_user(username="OpenToPublic", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="RegionalPDP", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="USTrainingCenter", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="NorCalEvents", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="TESTTeam", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="NationalCup", password=generateRandomPass()))
    specialTeams.append(User.objects.create_user(username="Tournament", password=generateRandomPass()))

    print("Loading Teams/Users:")

    _users = session.query(_User).all()
    for _user in _users:
        print("\t{}".format(_user.username))

        user = User.objects.create_user(username=_user.username, email=_user.email, first_name=_user.first_name, last_name=_user.last_name, password="password")
        if _user.is_superuser:
            print("\t\tIs a superuser!")

            user.is_superuser = True
            user.is_staff = True
            user.save()
        else:
            team_profile = TeamProfile(team=user)
            team_profile.save()

# Load Fields
def loadFields():
    print("Loading Fields:")

    _fields = session.query(_Field).all()
    for _field in _fields:
        print("\t{}".format(_field.name))
        print("\t\tField Times:")

        if Field.objects.filter(name=_field.name).count() == 0:
            field = Field(name=_field.name)
            field.save()
        else:
            field = Field.objects.filter(name=_field.name)[0]

        _fieldtimes = session.query(_FieldTime).filter(_FieldTime.field_id == _field.id)
        for _fieldtime in _fieldtimes:
            print("\t\t\t{}-{}".format(str(_fieldtime.start_time), str(_fieldtime.end_time)))

            timeslot = TimeSlot(start_time=_fieldtime.start_time, end_time=_fieldtime.end_time, location=field)
            timeslot.save()

        print("\t\tTeams:")
        _teamfields = session.query(_TeamField).filter(_TeamField.field_id == _field.id)
        for _teamfield in _teamfields:
            field.teams.add(getMatchingTeam(_teamfield.team_id))
            print("\t\t\t{}".format(str(_teamfield.team_id)))

def loadReservations():
    print("Loading Reservations:")

    _events = session.query(_Event).all()
    for _event in _events:
        print("\tEvent ID: {}\tEvent Date: {}\tStart Time: {}\tEnd Time: {}".format(str(_event.id), str(_event.date), str(_event.start_time), str(_event.end_time)))

        team = session.query(_Team).get(_event.team_id).name
        field = Field.objects.filter(name=session.query(_Field).get(_event.field_id).name)[0]
        gametype = GameType.objects.get(type=session.query(_Gametype).get(_event.game_type_id).name)

        _additional = session.query(_Additional).filter(_Additional.event_id==_event.id)
        if _additional.count() != 0:
            game_number = _additional[0].game_number
            game_opponent = _additional[0].opponent
        else:
            game_number = 1
            game_opponent = "N/A"

        if _event.date >= date_bounds()['start']:
            if timezone.localtime(timezone.now()).date() <= _event.date and _event.passed:
                print("\t\tCanceled reservation!")
                continue

            start_time = _event.start_time
            end_time = _event.end_time

            try:
                timeslot = field.timeslot_set.get(start_time=start_time, end_time=end_time)
            except ObjectDoesNotExist:
                print("\t\tWarning! Timeslot does not exist! [{} - {}] for Field {}".format(str(start_time), str(end_time), str(field)))
                print("\t\tChoose a timeslot that exists:")
                for timeslot in field.timeslot_set.all():
                    print("\t\t\t{}: {}".format(timeslot.pk, str(timeslot)))

                answer = raw_input("\t\t\tGive ID/PK value or press any key to create new> ")

                try:
                    answer = int(answer)
                    timeslot = field.timeslot_set.get(pk=answer)
                    print("\t\t\tUsing Timeslot PK: {}".format(timeslot.pk))
                except (TypeError, ValueError, ObjectDoesNotExist):
                    print("\t\t\tCreating new timeslot...")
                    timeslot = TimeSlot(location=field, start_time=start_time, end_time=end_time)
                    timeslot.save()

            gametype = GameType.objects.get(type=session.query(_Gametype).get(_event.game_type_id).name)

            context = {
                'game_number': game_number,
                'game_opponent': game_opponent,

                'date': _event.date,
                'approved': _event.approved,

                'team': getMatchingTeam(_event.team_id),
                'location': field,
                'gametype': gametype,
                'timeslot': timeslot
            }
            reservation = Reservation(**context)
            reservation.save()
        elif _event.date < datetime.datetime.strptime('01/01/2000', "%d/%m/%Y").date():
            continue
        else:
            context = {
                'game_number': game_number,
                'game_opponent': game_opponent,

                'date': _event.date,
                'approved': _event.approved,

                'team': team,
                'location': field,
                'gametype': gametype,
                'start_time': _event.start_time,
                'end_time': _event.end_time
            }
            archived = ArchivedReservation(**context)
            archived.save()
class Command(BaseCommand):
    def handle(self, *args, **options):
        loadGametypes()
        loadTeams()
        loadFields()
        loadReservations()
