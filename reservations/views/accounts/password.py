from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from reservations.utils import message_errors

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()

            update_session_auth_hash(request, form.user)
            messages.success(request, "Modified password!")
        else:
            message_errors(request, form.errors)

    return redirect('account')
