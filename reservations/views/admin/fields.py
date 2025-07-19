from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, DELETION, CHANGE

from reservations.utils import message_errors, log_message
from reservations.decorators import superuser_required

from reservations.models import Field, TimeSlot
from reservations.forms import FieldForm, TimeSlotForm
from reservations.api.forms import APIFieldModifyTeamsForm

@superuser_required
def all_fields(request):
    field = Field.objects.filter(active=True).first()
    field_form = FieldForm()

    if field:
        return redirect('field', field_id=field.pk)

    return render(request, 'reservations/admin/fields/field.html', { 'field_form': field_form })

@superuser_required
def add_field(request):
    if request.method == 'POST':
        form = FieldForm(request.POST)

        if form.is_valid():
            field = form.save()
            log_message(request, field, ADDITION, "New Field: " + str(field))
            messages.success(request, "Created new field " + field.name + "!")

            return redirect('field', field_id=field.pk)
        else:
            message_errors(request, form.errors)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@superuser_required
def field(request, field_id):
    current_field = get_object_or_404(Field, pk=field_id)
    current_timeslots = current_field.timeslot_set.filter(active=True)
    current_teams = current_field.teams.filter(is_active=True).values_list('id', flat=True)

    all_fields = Field.objects.natsorted(include={ 'active': True })

    field_form = FieldForm()
    timeslot_form = TimeSlotForm()
    modify_teams_form = APIFieldModifyTeamsForm()

    context = {
        'current_field': current_field,
        'current_timeslots': current_timeslots,
        'current_teams': current_teams,
        'all_fields': all_fields,
        'field_form': field_form,
        'timeslot_form': timeslot_form,
        'modify_teams_form': modify_teams_form
    }

    return render(request, 'reservations/admin/fields/field.html', context)

@superuser_required
def change_field_name(request, field_id):
    if request.method == 'POST':
        field = get_object_or_404(Field, pk=field_id)
        form = FieldForm(request.POST, instance=field)

        if form.is_valid():
            form.save()
            log_message(request, field, CHANGE, "Modified Field Name: {}".format(field.name))
            messages.success(request, "Renamed field to <b>{}</b>!".format(escape(field.name)))
        else:
            message_errors(request, form.errors)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@superuser_required
def delete_field(request, field_id):
    field = get_object_or_404(Field, pk=field_id)

    log_message(request, field, DELETION, "Deleted Field: {}".format(field.name))
    messages.success(request, "Deleted field <b>{}</b>!".format(escape(field.name)), extra_tags="undo={}".format(reverse('recovery_field', kwargs={ 'field_id': field.pk })))

    # Deactivate this field
    field.active = False
    field.save()

    # Deactivate all timeslots of this field
    timeslots = field.timeslot_set.filter(active=True)
    for timeslot in timeslots:
        timeslot.active = False
        timeslot.save()

    return redirect('all_fields')

@superuser_required
def field_add_timeslot(request, field_id):
    if request.method == 'POST':
        field = get_object_or_404(Field, pk=field_id)
        timeslot = TimeSlot(location=field)
        form = TimeSlotForm(request.POST, instance=timeslot)

        if form.is_valid():
            form.save()
            log_message(request, timeslot, ADDITION, "Added Timeslot: {}".format(timeslot))
            messages.success(request, "Added timeslot!")
        else:
            message_errors(request, form.errors)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@superuser_required
def field_remove_timeslot(request, field_id, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)

    timeslot.active = False
    timeslot.save()

    log_message(request, timeslot, DELETION, "Deleted Timeslot: {}".format(timeslot))
    messages.success(request, "Deleted timeslot!")
    return redirect(request.META.get('HTTP_REFERER', '/'))
