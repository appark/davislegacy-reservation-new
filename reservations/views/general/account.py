from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from reservations.forms import EmailChangeForm

@login_required
def account(request):
    password_change_form = PasswordChangeForm(user=request.user)
    email_change_form = EmailChangeForm()
    return render(request, 'reservations/general/account.html', { 'password_change_form': password_change_form, 'email_change_form': email_change_form })
