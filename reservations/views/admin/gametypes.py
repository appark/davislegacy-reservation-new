from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.html import escape

from django.contrib.admin.models import ADDITION, DELETION

from reservations.utils import message_errors, log_message
from reservations.decorators import superuser_required

from reservations.models import GameType
from reservations.forms import GameTypeForm

@superuser_required
def all_gametypes(request):
    gametypes = GameType.objects.filter(active=True)
    form = GameTypeForm()

    return render(request, 'reservations/admin/gametypes.html', { 'gametypes': gametypes, 'form': form })

@superuser_required
def new_gametype(request):
    if request.method == 'POST':
        form = GameTypeForm(request.POST)

        if form.is_valid():
            gametype = form.save()
            log_message(request, gametype, ADDITION, "New Gametype: {}".format(gametype.type))
            messages.success(request, "Created new gametype <b>{}</b>!".format(escape(gametype.type)))
        else:
            message_errors(request, form.errors)
    return redirect('all_gametypes')

@superuser_required
def delete_gametype(request, gametype_id):
    gametype = get_object_or_404(GameType, pk=gametype_id)

    gametype.active = False
    gametype.save()

    log_message(request, gametype, DELETION, "Deleted Gametype: {}".format(gametype.type))
    messages.success(request, "Deleted gametype <b>{}</b>!".format(escape(gametype.type)), extra_tags="undo={} timeout=0".format(reverse('recovery_gametype', kwargs={ 'gametype_id': gametype.pk })))

    return redirect('all_gametypes')
