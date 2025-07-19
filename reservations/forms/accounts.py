from django import forms

class EmailChangeForm(forms.Form):
    new_email1 = forms.EmailField()
    new_email2 = forms.EmailField()

    def clean(self):
        cleaned_data = super(EmailChangeForm, self).clean()

        if cleaned_data.get('new_email1') != cleaned_data.get('new_email2'):
            self.add_error('new_email2', "The two email fields didn't match.")

    def save(self, user):
        user.email = self.cleaned_data.get('new_email1')
        user.save()
