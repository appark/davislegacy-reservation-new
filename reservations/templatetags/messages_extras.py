from django import template
from django.contrib.messages import ERROR, WARNING, SUCCESS
import json

register = template.Library()

@register.filter(name='parseMessage')
def parseMessage(message):
    if message.level == ERROR:
        msgType = "danger"
    elif message.level == WARNING:
        msgType = "warning"
    elif message.level == SUCCESS:
        msgType = "success"
    else:
        return ""

    text = message.message

    # Extra Tags Formatting:
    # "Key1=Value1 Key2=Value2 ..."
    if message.extra_tags:
        options = {}
        raw_options = message.extra_tags.split(' ')

        for raw_option in raw_options:
            raw_option = raw_option.split('=')
            options[raw_option[0]] = raw_option[1]

        return "createMessage(\"{}\", \"{}\", {});".format(msgType, text, json.dumps(options))
    else:
        return "createMessage(\"{}\", \"{}\");".format(msgType, text)
