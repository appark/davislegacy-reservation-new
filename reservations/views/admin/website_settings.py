from django.shortcuts import render, redirect
from django.contrib import messages
from reservations.models import ReservationToken
from reservations.utils import message_errors
from reservations.decorators import superuser_required
from reservations.forms import CalendarRangeForm, TimeoutForm, BlockForm, SiteConfigForm

@superuser_required
def website_settings(request):
    calendar_form = CalendarRangeForm()
    timeout_form = TimeoutForm()
    block_form = BlockForm()
    site_config_form = SiteConfigForm()
    return render(request, "reservations/admin/website_settings.html", { "calendar_form": calendar_form, "timeout_form": timeout_form, "block_form": block_form, "site_config_form": site_config_form })

@superuser_required
def edit_calendar(request):
    if request.method == "POST":
        form = CalendarRangeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Calendar range updated successfully!")
        else:
            message_errors(request, form)
    return redirect("website_settings")

@superuser_required
def edit_timeout(request):
    if request.method == "POST":
        form = TimeoutForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Timeout updated successfully!")
        else:
            message_errors(request, form)
    return redirect("website_settings")

@superuser_required
def edit_block(request):
    if request.method == "POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Block updated successfully!")
        else:
            message_errors(request, form)
    return redirect("website_settings")

@superuser_required
def edit_site_config(request):
    if request.method == "POST":
        form = SiteConfigForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Site configuration updated successfully!")
        else:
            message_errors(request, form)
    return redirect("website_settings")

@superuser_required
def edit_block_time(request):
    if request.method == "POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Block time updated successfully!")
        else:
            message_errors(request, form)
    return redirect("website_settings")

@superuser_required
def refresh_tokens(request):
    if request.method == "POST":
        ReservationToken.objects.all().delete()
        messages.success(request, "All tokens have been refreshed!")
    return redirect("website_settings")
