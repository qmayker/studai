from django import forms
from core.fields import MultipleFileField
from .models import TextItem, ImageItem


class TextContentForm(forms.ModelForm):
    class Meta:
        model = TextItem
        fields = ["text_content"]
        widgets = {
            "text_content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Type your text here..."}
            ),
        }


class ImageContentForm(forms.Form):
    image_content = MultipleFileField()
    template_name_div = 'chat/form/image_content.html'

