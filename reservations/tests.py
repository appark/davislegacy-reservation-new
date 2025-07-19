from django.test import TestCase
from datetime import datetime, timedelta

from reservations.forms import *
from reservations.models import *
from reservations.utils import get_object_or_none
from django.contrib.auth.models import User

class EmptyObject(object):
    pass

class ReservationTest(TestCase):
    def setUp(self):
        self.team = User.objects.create_user("test", 'jello@example.com', 'password')
        self.team.change_group("Team")

        self.other_team = User.objects.create_user("test2", 'jello@example.com', 'password')
        self.other_team.change_group("Team")

        self.field = Field(name="field")
        self.field.save()

        self.not_member_field = Field(name="field2")
        self.not_member_field.save()

        self.gametype = GameType(type="type")
        self.gametype.save()

        self.timeslot1 = TimeSlot(start_time=datetime.strptime("10:30", '%H:%M').time(), end_time=datetime.strptime("12:30", '%H:%M').time(), location=self.field)
        self.timeslot1.save()

        self.timeslot2 = TimeSlot(start_time=datetime.strptime("13:00", '%H:%M').time(), end_time=datetime.strptime("15:00", '%H:%M').time(), location=self.field)
        self.timeslot2.save()

        self.non_member_timeslot = TimeSlot(start_time=datetime.strptime("10:30", '%H:%M').time(), end_time=datetime.strptime("12:30", '%H:%M').time(), location=self.not_member_field)
        self.non_member_timeslot.save()

        self.field.teams.add(self.team)

    def test_editor_1_form(self):
        # Test whether form errors with nothing
        form = EditorStep1Form()
        self.assertFalse(form.is_valid())

        # Test whether a good form works
        good_fields = {
            'game_number': 1,
            'game_opponent': "Game Opponent",
            'gametype': self.gametype.pk,
            'team': self.team.pk,
            'date': datetime.now() + timedelta(days=10)
        }

        self.client.login(username='test', password='password')
        session = self.client.session;

        request = EmptyObject()
        request.session = session
        request.user = self.team

        form = EditorStep1Form(good_fields, user=request.user)
        form.populate_form(request)

        self.assertTrue(form.is_valid())

    def test_editor_2_form(self):
        # Setup a fake session
        self.client.login(username='test', password='password')
        session = self.client.session

        request = EmptyObject()
        request.user = self.team
        request.session = session

        session['resv_team'] = self.team.pk
        session['resv_date'] = "01/01/2016"

        # Test whether form errors with nothing
        form = EditorStep2Form()
        form.populate_form(request)
        self.assertFalse(form.is_valid())

        # Test whether a good form works
        form = EditorStep2Form({
            'timeslot': self.timeslot1.pk
        })
        form.populate_form(request)
        self.assertTrue(form.is_valid())

        # Test whether a bad form fails (bad timeslot)
        form = EditorStep2Form({
            'timeslot': self.non_member_timeslot.pk
        })
        form.populate_form(request)
        self.assertFalse(form.is_valid())

        # Test whether another bad form fails (timeslot occupied already)
        data = {
            'game_number': 1,
            'game_opponent': "Game Opponent",
            'gametype': self.gametype,
            'date': datetime.strptime("01/01/2016", "%m/%d/%Y").date(),
            'team': self.team,
            'location': self.field,
            'timeslot': self.timeslot2
        }

        reservation = Reservation(**data)
        reservation.save()
        form = EditorStep2Form({
            'timeslot': self.timeslot2.pk
        })
        form.populate_form(request)
        self.assertFalse(form.is_valid())

        # Check whether we can create a custom timeslot
        request.user.change_group("Superuser")
        request.user.is_superuser = True

        form = EditorStep2Form({
            'custom_timeslot': True,
            'start_time': "14:00",
            'end_time': "16:00",
            'field': self.field.pk
        })

        form.populate_form(request)
        self.assertTrue(form.is_valid())

        form.populate_session(request)
        timeslot = get_object_or_none(TimeSlot, pk=request.session['resv_timeslot'])
        self.assertTrue(timeslot != None)
        self.assertTrue(timeslot.start_time == datetime.strptime("14:00", '%H:%M').time())
        self.assertTrue(timeslot.end_time == datetime.strptime("16:00", '%H:%M').time())
        self.assertTrue(timeslot.active == False)

        data = {
            'game_number': 1,
            'game_opponent': "Game Opponent",
            'gametype': self.gametype,
            'date': datetime.strptime("01/01/2016", "%m/%d/%Y").date(),
            'team': self.team,
            'location': self.field,
            'timeslot': timeslot
        }
        custom_reservation = Reservation(**data)
