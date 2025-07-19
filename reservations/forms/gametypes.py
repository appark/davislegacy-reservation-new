from django.forms import ModelForm

from reservations.models import GameType

class GameTypeForm(ModelForm):
    class Meta:
        model = GameType
        fields = ['type']
        error_messages = {
            'type': {
                'required': "Please give a gametype!",
                'max_length': "This gametype is too long! Try again!"
            }
        }
