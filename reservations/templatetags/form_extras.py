from django import template

register = template.Library()

def get_field_context(field, *args, **kwargs):
    id = kwargs.pop('id', None)
    required = kwargs.pop('required', False)
    label = kwargs.pop('label', field.label)
    placeholder = kwargs.pop('placeholder', None)

    # Get the field value - for BoundField, use the value() method
    if hasattr(field, 'value') and callable(field.value):
        default_value = field.value()
    else:
        default_value = getattr(field.field, 'initial', None)
    value = kwargs.pop('value', default_value)

    poptext = kwargs.pop('poptext', None)

    group_extras = kwargs.pop('group_extras', None)
    extras = kwargs.pop('extras', None)

    return { 'field': field, 'id': id, 'required': required, 'label': label, 'placeholder': placeholder, 'value': value, 'poptext': poptext, 'group_extras': group_extras, 'extras': extras }

@register.inclusion_tag('reservations/layouts/tags/text_field.html', name='textField')
def text_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['field_type'] = 'text'

    return context

@register.inclusion_tag('reservations/layouts/tags/text_field.html', name='numberField')
def number_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['field_type'] = 'number'

    return context

@register.inclusion_tag('reservations/layouts/tags/text_field.html', name='emailField')
def email_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['field_type'] = 'email'

    return context

@register.inclusion_tag('reservations/layouts/tags/text_field.html', name='passwordField')
def password_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['field_type'] = 'password'

    return context

@register.inclusion_tag('reservations/layouts/tags/date_field.html', name='dateField')
def date_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    # Format date value if it's a date object
    if context['value'] and hasattr(context['value'], 'strftime'):
        context['value'] = context['value'].strftime('%m/%d/%Y')
    return context

@register.inclusion_tag('reservations/layouts/tags/select_field.html', name='selectField')
def select_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    return context

@register.inclusion_tag('reservations/layouts/tags/multiple_select_field.html', name='multipleSelectField')
def multiple_select_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['value'] = [] if not context['value'] else context['value']
    return context

@register.inclusion_tag('reservations/layouts/tags/dynamic_select_field.html', name='dynamicSelectField')
def dynamic_select_field(field, *args, **kwargs):
    context = get_field_context(field, *args, **kwargs)
    context['value'] = [] if not context['value'] else context['value']
    return context

@register.filter(name='normalizeInput')
def normalize_input(input_val):
    """
    Converts input to int if possible, otherwise returns input
    """
    try:
        return int(input_val)
    except ValueError:
        return input_val
