from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, CHANGE

from reservations.decorators import token_required
from reservations.utils import message_errors, clear_tokens, get_object_or_none, send_email, send_email_superusers, log_message, is_superuser, is_manager

from django.contrib.auth.models import User
from reservations.models import Reservation, GameType, Field, TimeSlot, Tournament
from reservations.forms import EditorStep1Form, EditorStep2Form
from reservations.utils import has_reservation_block

@login_required
def editor_step1(request):
    if request.session.get('resv_step', -1) < 1:
        messages.error(request, "An invalid editor environment was detected! Please try again!")
        return redirect('dashboard')

    if request.method == 'POST':
        if is_superuser(request.user):
            form = EditorStep1Form(request.POST)
        else:
            form = EditorStep1Form(request.POST, user=request.user)

        form.populate_form(request)

        if form.is_valid():

            # Check and make sure there are not editor blocks on this page
            if has_reservation_block(request, form.cleaned_data.get('date')):
                messages.error(request, "You cannot create/modify a reservation on this date, because today's date is too close to it. Please choose another date.")
            else:
                form.populate_session(request)
                request.session['resv_step'] = 2
                return redirect('editor_step2')
        else:
            message_errors(request, form.errors)
    else:
        # Superusers don't need an assigned team
        if is_superuser(request.user):
            form = EditorStep1Form()
        else:
            form = EditorStep1Form(user=request.user)
        form.populate_form(request)

    return render(request, 'reservations/general/editor/step1.html', { 'form': form, 'type': request.session.get('resv_tokentype', None) })

@login_required
@token_required()
def editor_step2(request):
    if request.session.get('resv_step', -1) < 2:
        return redirect('editor_step1')

    if request.method == 'POST':
        form = EditorStep2Form(request.POST)
        if not form.populate_form(request):
            messages.error(request, "There was something wrong with the reservation data. Try completing the form again!")
            return redirect('editor_step1')

        if form.is_valid():
            if not form.populate_session(request):
                messages.error(request, "There was something wrong with the reservation data. Try completing the form again!")
                return redirect('editor_step1')
            request.session['resv_step'] = 3

            # People in edit mode don't need a confirmation page.
            if request.session.get('resv_tokentype') == "edit":
                return redirect('editor_complete')

            return redirect('editor_step3')
        else:
            message_errors(request, form.errors)
    else:
        form = EditorStep2Form()
        if not form.populate_form(request):
            messages.error(request, "There was something wrong with the reservation data. Try completing the form again!")
            return redirect('editor_step1')
    return render(request, 'reservations/general/editor/step2.html', { 'form': form, 'type': request.session.get('resv_tokentype', None) })

@login_required
@token_required(timeout_msg=True)
def editor_step3(request):
    if request.session.get('resv_step', -1) < 3:
        return redirect('editor_step2')

    resv_date = request.session.get('resv_date', None)
    if resv_date:
        resv_date = datetime.strptime(resv_date, "%m/%d/%Y").date()

    context = {
        'team': get_object_or_none(User, pk=request.session.get('resv_team', -1)),
        'game_number': request.session.get('resv_game_number', None),
        'game_opponent': request.session.get('resv_game_opponent', None),
        'timeslot': get_object_or_none(TimeSlot, pk=request.session.get('resv_timeslot', -1)),
        'date': resv_date,
        'location': get_object_or_none(Field, pk=request.session.get('resv_location', -1)),
        'gametype': get_object_or_none(GameType, pk=request.session.get('resv_gametype', -1)),
        'gender': request.session.get('resv_gender', None),
        'age': request.session.get('resv_age', None)
    }

    return render(request, 'reservations/general/editor/step3.html', context)

@login_required
@token_required(timeout_msg=True)
@transaction.atomic
def editor_complete(request):
    # Get objects/strings from session
    resv_date = request.session.get('resv_date', None)
    if resv_date:
        resv_date = datetime.strptime(resv_date, "%m/%d/%Y").date()

    context = {
        'team': get_object_or_none(User, pk=request.session.get('resv_team', -1)),
        'game_number': request.session.get('resv_game_number', None),
        'game_opponent': request.session.get('resv_game_opponent', None),
        'timeslot': get_object_or_none(TimeSlot, pk=request.session.get('resv_timeslot', -1)),
        'date': resv_date,
        'location': get_object_or_none(Field, pk=request.session.get('resv_location', -1)),
        'gametype': get_object_or_none(GameType, pk=request.session.get('resv_gametype', -1)),
        'gender': request.session.get('resv_gender', None),
        'age': request.session.get('resv_age', None)
    }

    # Check if data all made it through.
    if not all([context['team'], context['game_opponent'], context['timeslot'], context['date'], context['location'], context['gametype']]) or context['game_number'] == None:
        messages.error(request, "There was something wrong with the reservation data. Try completing the form again!")
        return redirect('editor_step1')

    # Is there a reservation block?
    if has_reservation_block(request, context['date']):
        messages.error(request, "You cannot create/modify a reservation on this date, because today's date is too close to it. Please choose another timeslot! (Note: This time conflict is not supposed to occur. Please tell an administrator about this event!)")
        return redirect('editor_step1')

    # Is this timeslot even avaliable?
    if context['timeslot'].reservation_set.filter(active=True, date=context['date']).exclude(pk=request.session.get('resv_id', -1)).count() > 0:
        messages.error(request, "This timeslot has already been reserved. Please choose another timeslot! (Note: This time conflict is not supposed to occur. Please tell an administrator about this event!)")
        return redirect('editor_step2')

    # Does this team have permission to use this game type?
    # TODO
    # if False:
    #     messages.error(request, "Your team does not have permission to use this game type.  Please choose another game type!")
    #     return redirect('editor_step1')

    if Tournament.objects.filter(active=True, start_date__lte=context['date'], end_date__gte=context['date'], locations=context['location']).count() > 0:
        messages.error(request, "There is a tournament on this date. Please choose another timeslot! (Note: This time conflict is not supposed to occur. Please tell an administrator about this event!)")
        return redirect('editor_step2')

    # Save the reservations (either by creating a new reservation or saving an existing one)
    if request.session.get('resv_tokentype') == "edit":
        reservation = get_object_or_404(Reservation, pk=request.session.get('resv_id', -1))

        # Check to make sure that the original reservation doesn't have a block on it too
        if has_reservation_block(request, reservation.date):
            messages.error(request, "You cannot create/modify a reservation on this date, because today's date is too close to it. Please choose another timeslot! (Note: This time conflict is not supposed to occur. Please tell an administrator about this event!)")
            return redirect('editor_step1')

        reservation.game_number = context['game_number']
        reservation.game_opponent = context['game_opponent']
        reservation.date = context['date']
        reservation.team = context['team']
        reservation.location = context['location']
        reservation.gametype = context['gametype']
        reservation.timeslot = context['timeslot']
        reservation.gender = context['gender']
        reservation.age = context['age']

        if not is_superuser(request.user):
            # Only email if they're not a superuser
            # First, check if they are a manager. If they are not a manager, email the team.
            if is_manager(request.user) and request.user.email:
                send_email("Modified Reservation: {}".format(reservation), 'reservations/email/edit_reservation.html', { 'reservation': reservation }, [request.user.email])
            elif reservation.team.email:
                send_email("Modified Reservation: {}".format(reservation), 'reservations/email/edit_reservation.html', { 'reservation': reservation }, [reservation.team.email])

            send_email_superusers("Modified Reservation: {}".format(reservation), 'reservations/email/approve_reservation_edit.html', { 'reservation': reservation, 'link': reverse('all_reservations') })
            reservation.approved = False

            messages.success(request, "Saved reservation <b>{}</b>! This reservation will have to be reapproved.".format(escape(str(reservation))))
        else:
            messages.success(request, "Saved reservation <b>{}</b>!".format(escape(str(reservation))))

        reservation.save()

        # Log change to admin
        log_message(request, reservation, CHANGE, "Modified Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))
    else:
        reservation = Reservation(**context)
        reservation.save()

        # Log addition to admin
        log_message(request, reservation, ADDITION, "New Reservation: {} on {}".format(reservation, reservation.date.strftime('%m/%d/%Y')))

        if is_manager(request.user) and request.user.email:
            send_email("New Reservation: {}".format(reservation), 'reservations/email/new_reservation.html', { 'reservation': reservation }, [request.user.email])
        elif reservation.team.email:
            send_email("New Reservation: {}".format(reservation), 'reservations/email/new_reservation.html', { 'reservation': reservation }, [reservation.team.email])

        send_email_superusers("New Reservation: {}".format(reservation), 'reservations/email/approve_reservation.html', { 'reservation': reservation, 'link': reverse('all_reservations') })

        messages.success(request, "Created reservation <b>{}</b>! This reservation will have to be approved.".format(escape(str(reservation))))

    # Clear the tokens so other people can make reservations
    clear_tokens(request)

    # If there was a next, send them there
    resv_next = request.session.get('resv_next', None)
    if resv_next:
        request.session.pop('resv_next', None)
        return redirect(resv_next)

    return redirect('my_reservations')
