from django import forms
from .models import TextItem, Content


class TextContentForm(forms.ModelForm):
    class Meta:
        model = TextItem
        fields = ["text_content"]
        widgets = {
            "text_content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Type your message here..."}
            ),
        }
