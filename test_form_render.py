#!/usr/bin/env python

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo2.settings')
django.setup()

from reservations.forms.editor import EditorStep1Form
from reservations.models import Reservation
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.template import Context, Template

def test_form_rendering():
    # Get a reservation to test with
    reservation = Reservation.objects.first()
    if not reservation:
        print("No reservations found")
        return
    
    print(f"Testing form rendering for reservation {reservation.pk}")
    
    # Create form like the view does
    form = EditorStep1Form()
    
    # Set up session data
    factory = RequestFactory()
    request = factory.get('/')
    request.session = SessionStore()
    request.session['resv_team'] = reservation.team.pk
    request.session['resv_gametype'] = reservation.gametype.pk
    request.session['resv_game_number'] = reservation.game_number
    request.session['resv_game_opponent'] = reservation.game_opponent
    request.session['resv_date'] = reservation.date.strftime('%m/%d/%Y')
    
    # Populate form
    form.populate_form(request)
    
    # Test simple HTML rendering
    print("\n=== TEAM FIELD HTML ===")
    print(f"Field choices count: {len(list(form.fields['team'].choices))}")
    print(f"Field initial: {form.fields['team'].initial}")
    
    # Render the team field manually to see HTML
    team_field = form['team']
    print("Team field HTML snippet:")
    print(str(team_field)[:500] + "...")
    
    # Check if our value appears in the HTML
    if f'value="{reservation.team.pk}"' in str(team_field):
        print("✓ Team PK found in HTML")
    else:
        print("✗ Team PK NOT found in HTML")
        
    if 'selected' in str(team_field):
        print("✓ 'selected' attribute found in HTML")
    else:
        print("✗ 'selected' attribute NOT found in HTML")
    
    print("\n=== GAMETYPE FIELD HTML ===")
    gametype_field = form['gametype']
    print("Gametype field HTML:")
    print(str(gametype_field))
    
    if f'value="{reservation.gametype.pk}"' in str(gametype_field):
        print("✓ Gametype PK found in HTML")
    else:
        print("✗ Gametype PK NOT found in HTML")
        
    if 'selected' in str(gametype_field):
        print("✓ 'selected' attribute found in gametype HTML")
    else:
        print("✗ 'selected' attribute NOT found in gametype HTML")

if __name__ == "__main__":
    test_form_rendering()