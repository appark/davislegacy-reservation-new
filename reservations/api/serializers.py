from rest_framework import serializers
from django.contrib.auth.models import User
from reservations.models import Reservation, Tournament, TimeSlot

class TimeSlotSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(read_only=True, format="%I:%M %p")
    end_time = serializers.TimeField(read_only=True, format="%I:%M %p")

    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']

class SimpleTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fullname']

class ReservationSerializer(serializers.ModelSerializer):
    timeslot = TimeSlotSerializer()
    team = SimpleTeamSerializer()

    location = serializers.StringRelatedField()
    gametype = serializers.StringRelatedField()
    title = serializers.ReadOnlyField(source='__unicode__')
    date = serializers.DateField(read_only=True, format="%b. %d, %Y")

    class Meta:
        model = Reservation
        exclude = ['active', 'approved']

class TournamentSerializer(serializers.ModelSerializer):
    gametype = serializers.StringRelatedField(read_only=True)
    locations = serializers.StringRelatedField(read_only=True, many=True)
    start_date = serializers.DateField(read_only=True, format="%b. %d, %Y")
    end_date = serializers.DateField(read_only=True, format="%b. %d, %Y")

    class Meta:
        model = Tournament
        exclude = ['active']

class SimpleReservationSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='__unicode__')
    date = serializers.DateField(read_only=True, format="%b. %d, %Y")

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date', 'approved']

class TeamSerializer(serializers.ModelSerializer):
    reservation_set = SimpleReservationSerializer(many=True)
    reservation_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['fullname', 'reservation_count', 'reservation_set']

    def get_reservation_count(self, obj):
        return obj.reservation_set.count()
