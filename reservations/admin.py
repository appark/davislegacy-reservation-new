from django.contrib import admin
from reservations.forms.fields import TimeSlotForm
from django.contrib.admin.models import LogEntry, DELETION
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from reservations.models import Field, TimeSlot, GameType, Tournament, ArchivedTournament, Reservation, ArchivedReservation, WebsiteSetting, TeamProfile

# Register all models to the Django admin site
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']

admin.site.register(Field, FieldAdmin)

class GametypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'active']

admin.site.register(GameType, GametypeAdmin)

class TimeSlotAdmin(admin.ModelAdmin):
    form = TimeSlotForm
    def start_time_formatted(self, obj):
        return obj.start_time.strftime('%I:%M %p').upper()

    def end_time_formatted(self, obj):
        return obj.end_time.strftime('%I:%M %p').upper()

    start_time_formatted.admin_order_field = "start_time"
    start_time_formatted.short_description = "Start Time"
    end_time_formatted.admin_order_field = "end_time"
    end_time_formatted.short_description = "End Time"

    list_display = ['location', 'start_time_formatted', 'end_time_formatted', 'active']

admin.site.register(TimeSlot, TimeSlotAdmin)

class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'active']

admin.site.register(Tournament, TournamentAdmin)

class ArchivedTournamentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'start_date', 'end_date', 'gametype', 'locations']
    list_display = ['name', 'start_date', 'end_date']

admin.site.register(ArchivedTournament, ArchivedTournamentAdmin)

class ReservationAdmin(admin.ModelAdmin):
    def date_formatted(self, obj):
        return obj.date.strftime('%m/%d/%Y')

    def location_formatted(self, obj):
        return obj.location.name

    def start_time_formatted(self, obj):
        return obj.timeslot.start_time.strftime('%I:%M %p').upper()

    def end_time_formatted(self, obj):
        return obj.timeslot.end_time.strftime('%I:%M %p').upper()

    date_formatted.admin_order_field = 'date'
    date_formatted.short_description = "Date"
    location_formatted.admin_order_field = 'location'
    location_formatted.short_description = "Location"
    start_time_formatted.admin_order_field = "timeslot__start_time"
    start_time_formatted.short_description = "Start Time"
    end_time_formatted.admin_order_field = "timeslot__end_time"
    end_time_formatted.short_description = "End Time"

    search_fields = ['team__username', 'date', 'location__name', 'gametype__type', 'game_number', 'game_opponent', 'timeslot__start_time', 'timeslot__end_time', 'age', 'gender']
    list_filter = [('team', admin.RelatedOnlyFieldListFilter)]
    list_display = ['__str__', 'team', 'date_formatted', 'location_formatted', 'gametype', 'game_number', 'game_opponent', 'start_time_formatted', 'end_time_formatted', 'approved', 'active', 'age', 'gender']

admin.site.register(Reservation, ReservationAdmin)

class ArchivedReservationAdmin(admin.ModelAdmin):
    def date_formatted(self, obj):
        return obj.date.strftime('%m/%d/%Y')

    def start_time_formatted(self, obj):
        return obj.start_time.strftime('%I:%M %p').upper()

    def end_time_formatted(self, obj):
        return obj.end_time.strftime('%I:%M %p').upper()

    date_formatted.admin_order_field = 'date'
    date_formatted.short_description = "Date"
    start_time_formatted.admin_order_field = "start_time"
    start_time_formatted.short_description = "Start Time"
    end_time_formatted.admin_order_field = "end_time"
    end_time_formatted.short_description = "End Time"

    search_fields = ['team', 'date', 'location', 'gametype', 'game_number', 'game_opponent', 'start_time', 'end_time', 'age', 'gender']
    list_display = ['__str__', 'team', 'date_formatted', 'location', 'gametype', 'game_number', 'game_opponent', 'start_time_formatted', 'end_time_formatted', 'approved', 'deleted', 'age', 'gender']

admin.site.register(ArchivedReservation, ArchivedReservationAdmin)

class LogEntryAdmin(admin.ModelAdmin):
    def object_link(self, obj):
        ct = obj.content_type
        if obj.action_flag == DELETION or not ct:
            return "N/A"
        else:
            return "<a href=\"%s\">Click to edit object</a>" % reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id])

    object_link.allow_tags = True
    object_link.short_description = "Modify Object"

    search_fields = ['user__username', 'change_message']
    list_display = ['change_message', 'object_link', 'action_time', 'user', 'content_type']

admin.site.register(LogEntry, LogEntryAdmin)

class WebsiteSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'description', 'value']

admin.site.register(WebsiteSetting, WebsiteSettingAdmin)

class TeamProfileInline(admin.TabularInline):
    model = TeamProfile
    can_delete = False

    verbose_name = "Edit Additional Team Information"
    verbose_name_plural = "Edit Additional Team Information"

class TeamAdmin(UserAdmin):
    def fullname_formatted(self, obj):
        return obj.fullname
    fullname_formatted.short_description = "Fullname"

    def group_formatted(self, obj):
        return obj.groups.first()
    group_formatted.short_description = "Group"

    inlines = [TeamProfileInline]
    list_display = ['username', 'fullname_formatted', 'email', 'first_name', 'last_name', 'group_formatted', 'is_superuser']

admin.site.unregister(User)
admin.site.register(User, TeamAdmin)
