from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group

from natsort import natsorted

# TODO: Make this a permanent fix by performing database migrations
GENDER_CHOICES = (
    ('boys', 'Male'),
    ('girls', 'Female')
)

# Field Model
class FieldManager(models.Manager):
    # Natural sorts field names
    def natsorted(self, *args, **kwargs):
        choice_format = kwargs.pop('format', None)

        include = kwargs.pop('include', {})
        exclude = kwargs.pop('exclude', {})
        q_objects = kwargs.pop('q_objects', None)

        if choice_format:
            def sorter(field):
                return field[1]
            if choice_format == 'tuple':
                return natsorted(super(FieldManager, self).get_queryset().filter(**include).exclude(**exclude).distinct().values_list('id', 'name'), key=sorter)
            elif choice_format == 'q_tuple':
                return natsorted(super(FieldManager, self).get_queryset().filter(q_objects).exclude(**exclude).distinct().values_list('id', 'name'), key=sorter)
        else:
            def sorter(field):
                return field['name']
            return natsorted(super(FieldManager, self).get_queryset().filter(**include).exclude(**exclude).distinct().values('pk', 'name'), key=sorter)

class Field(models.Model):
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=2048)
    teams = models.ManyToManyField(User)

    def __str__(self):
        return str(self.name)

    objects = FieldManager()

    class Meta:
        ordering = ['name']

# TimeSlot Model
class TimeSlot(models.Model):
    active = models.BooleanField(default=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    location = models.ForeignKey(Field, on_delete=models.CASCADE)

    # Whether this timeslot overlaps with other (custom) timeslots
    overlap = models.ManyToManyField('self')

    def __str__(self):
        return "{} - {} @ {}".format(self.start_time.strftime("%g %P"), self.end_time.strftime("%g %P"), self.location)

    class Meta:
        ordering = ['start_time']

# GameType Model
class GameType(models.Model):
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=2048)
    teams = models.ManyToManyField(User)

    def __str__(self):
        return str(self.type)

    class Meta:
        ordering = ['type']

# Tournament Model
class Tournament(models.Model):
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=2048)

    start_date = models.DateField()
    end_date = models.DateField()

    gametype = models.ForeignKey(GameType, on_delete=models.PROTECT, null=True, blank=True)
    locations = models.ManyToManyField(Field)

    def __str__(self):
        return "{}: {} to {}".format(self.name, self.start_date.strftime('%m/%d/%Y'), self.end_date.strftime('%m/%d/%Y'))

    class Meta:
        ordering = ['start_date']

class ArchivedTournament(models.Model):
    name = models.CharField(max_length=2048)
    start_date = models.DateField()
    end_date = models.DateField()
    gametype = models.CharField(max_length=2048)
    locations = models.TextField()

    def __str__(self):
        return "{}: {} to {}".format(self.name, self.start_date.strftime('%m/%d/%Y'), self.end_date.strftime('%m/%d/%Y'))

# Reservation Model
class Reservation(models.Model):
    active = models.BooleanField(default=True)

    game_number = models.IntegerField()
    game_opponent = models.CharField(max_length=2048)

    date = models.DateField()
    approved = models.BooleanField(default=False)

    # Raises ProtectedError if something tries to delete.
    team = models.ForeignKey(User, on_delete=models.PROTECT)
    location = models.ForeignKey(Field, on_delete=models.PROTECT)
    gametype = models.ForeignKey(GameType, on_delete=models.PROTECT)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    age = models.CharField(max_length=10)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='boys')

    def __str__(self):
        return "{} @ {}".format(self.team.fullname, self.location.name)

    class Meta:
        ordering = ['date', 'location__name', 'timeslot__start_time']

# Archived Reservation Model
class ArchivedReservation(models.Model):
    game_number = models.IntegerField()
    game_opponent = models.CharField(max_length=2048)
    date = models.DateField()
    approved = models.BooleanField()
    team = models.CharField(max_length=2048)
    location = models.CharField(max_length=2048)
    gametype = models.CharField(max_length=2048)
    start_time = models.TimeField()
    end_time = models.TimeField()
    deleted = models.BooleanField(default=False)
    age = models.CharField(max_length=10)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='boys')

    def __str__(self):
        return "{} @ {}".format(self.team, self.location)

# Reservation Token (used to prevent multiple reservations at one time)
class ReservationToken(models.Model):
    team = models.ForeignKey(User, on_delete=models.CASCADE)
    issued = models.DateTimeField(auto_now_add=True)
    hold_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Issued to {} at {}".format(self.team, self.issued)

# Website Settings
class WebsiteSetting(models.Model):
    key = models.CharField(max_length=2048, unique=True)
    description = models.CharField(max_length=2048)
    value = models.CharField(max_length=2048)

    def __str__(self):
        return str(self.key)

# Team Profile
class TeamProfile(models.Model):
    team = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='profile')
    description = models.CharField(max_length=2048, null=True, blank=True)
    age = models.CharField(max_length=10)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default="boys")

    def __str__(self):
        return str(self.team)

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='manager_profile')
    teams = models.ManyToManyField(User, related_name='manager')

    def __str__(self):
        return str(self.user)

# Add Extra Functionality to the User Model
# Returns the username and a description (if it exists)
@property
def fullname(self):
    if hasattr(self, 'profile') and self.profile.description:
        return str(self.username) + " (" + str(self.profile.description) + ")"
    return str(self.username)

# Adds/Removes the specified group (string)
def change_group(self, group):
    group = Group.objects.get(name=group)
    self.groups.clear()
    self.groups.add(group)
User.add_to_class("fullname", fullname)
User.add_to_class("change_group", change_group)
