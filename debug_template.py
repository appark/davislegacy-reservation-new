#!/usr/bin/env python

import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo2.settings')
django.setup()

from django.template import Template, Context
from reservations.forms.editor import EditorStep1Form
from reservations.models import Reservation
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore

# Set up form
reservation = Reservation.objects.first()
form = EditorStep1Form()
factory = RequestFactory()
request = factory.get('/')
request.session = SessionStore()
request.session['resv_team'] = reservation.team.pk
request.session['resv_gametype'] = reservation.gametype.pk
form.populate_form(request)

# Create a debug template that shows what's happening
debug_template = '''
{% load form_extras %}
<div class="debug">
Field: {{ field.name }}
Value: {{ value }}
Value type: {{ value|default:"None" }}
Choices:
{% for choice_value, choice_label in field.field.choices %}
  Choice {{ choice_value }} ({{ choice_label }}) - Match: {% if value|normalizeInput == choice_value|normalizeInput %}YES{% else %}NO{% endif %}
{% endfor %}
</div>

{{ field.field.choices|length }} choices total
'''

template = Template(debug_template)

# Get the field context manually
from reservations.templatetags.form_extras import get_field_context
team_field = form['team']
context_data = get_field_context(team_field, required=True, label='Team')

context = Context(context_data)
result = template.render(context)
print("=== DEBUG TEMPLATE OUTPUT ===")
print(result)