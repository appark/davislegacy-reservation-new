from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, DELETION

from django.contrib.auth.models import User
from reservations.decorators import superuser_required
from reservations.utils import log_message, message_errors
from reservations.forms import CreateSuperuserForm, CreateManagerForm
from reservations.api.forms import APIManagerModifyTeamsForm

@superuser_required
def all_managers(request):
    superusers = User.objects.filter(groups__name='Superuser')
    managers = User.objects.filter(groups__name='Manager').select_related('manager_profile')

    for manager in managers:
        manager.teams = manager.manager_profile.teams.filter(is_active=True).values_list('id', flat=True)

    superuser_form = CreateSuperuserForm()
    manager_form = CreateManagerForm()

    modify_teams_form = APIManagerModifyTeamsForm()

    return render(request, 'reservations/admin/managers.html', {
        'superusers': superusers,
        'managers': managers,
        'superuser_form': superuser_form,
        'manager_form': manager_form,
        'modify_teams_form': modify_teams_form
    })

def delete_user(request, user_id, access_level):
    user = get_object_or_404(User, pk=user_id)

    log_message(request, user, DELETION, "Deleted {}: {}".format(access_level.capitalize(), user.username))
    messages.success(request, "Deleted {} <b>{}</b>!".format(access_level, escape(user.username)))

    user.delete()

@superuser_required
def remove_manager(request, user_id):
    delete_user(request, user_id, 'manager')
    return redirect('all_managers')

@superuser_required
def remove_superuser(request, user_id):
    delete_user(request, user_id, 'superuser')
    return redirect('all_managers')

def add_user(request, form_class, access_level):
    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            user = form.save()

            log_message(request, user, ADDITION, "Added {}: {}".format(access_level.capitalize(), user.username))
            messages.success(request, "Added {} <b>{}</b>!".format(access_level, escape(user.username)))
        else:
            message_errors(request, form.errors)

@superuser_required
def new_manager(request):
    add_user(request, CreateManagerForm, 'manager')
    return redirect('all_managers')

@superuser_required
def new_superuser(request):
    add_user(request, CreateSuperuserForm, 'superuser')
    return redirect('all_managers')
