from django import template
from django.utils import timezone
from django.conf import settings
import re

from reservations.models import Reservation
from reservations.utils import is_superuser

register = template.Library()

@register.filter(name='firstLetter')
def firstLetter(username):
    return username.upper()[0]

@register.simple_tag(name='resvCount', takes_context=True)
def resv_count(context):
    request = context['request']
    if request.user.is_authenticated:
        if is_superuser(request.user):
            count = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), approved=False).count()
        else:
            count = Reservation.objects.filter(active=True, date__gte=timezone.localtime(timezone.now()).date(), team=request.user).count()
        return str(count)
    return 0

@register.tag(name='active')
def active(parser, token):
    try:
        arguments = token.split_contents()
        pattern = arguments[1]

    except ValueError:
        raise template.TemplateSyntaxError("%r requires a pattern as an argument." % token.contents.split[0])

    if not (pattern[0] == pattern[-1] and pattern[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's pattern should be in quotes." % token.contents.split[0])

    nodelist = parser.parse(('endactive',))
    parser.delete_first_token()

    return IsActiveNode(pattern[1:-1], nodelist)

class IsActiveNode(template.Node):
    def __init__(self, pattern, nodelist):
        self.pattern = pattern
        self.nodelist = nodelist

    # Checks if the regex matches. Adds optional backslash to end.
    def render(self, context):
        request = context['request']
        path = request.get_full_path()

        # Remove FORCE_SCRIPT_NAME prefix from the path, if necessary
        if hasattr(settings, "FORCE_SCRIPT_NAME") and settings.FORCE_SCRIPT_NAME:
            prefix = settings.FORCE_SCRIPT_NAME
            path = path[len(prefix):]

        if re.search(self.pattern, path):
            return self.nodelist.render(context)
        return ""
