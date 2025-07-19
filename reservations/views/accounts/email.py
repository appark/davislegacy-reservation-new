from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import escape

from reservations.forms import EmailChangeForm
from reservations.utils import message_errors

@login_required
def change_email(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST)

        if form.is_valid():
            form.save(request.user)
            messages.success(request, "Modified email to <b>{}</b>!".format(escape(form.cleaned_data.get('new_email1'))))
        else:
            message_errors(request, form.errors)

    return redirect('account')
