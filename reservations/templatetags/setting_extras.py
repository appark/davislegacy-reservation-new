from django import template
from django.conf import settings
from reservations.utils import get_website_setting

register = template.Library()

@register.simple_tag(name='getSetting')
def get_setting(key):
    if hasattr(settings, key):
        return getattr(settings, key, "")
    else:
        return get_website_setting(key, "")
