from django import forms


class AttemptForm(forms.Form):
    attempt_id = forms.IntegerField()
