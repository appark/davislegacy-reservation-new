from django import template
import datetime

register = template.Library()

@register.filter(name='makeInclusive')
def make_inclusive(date):
    return date + datetime.timedelta(days=1)
