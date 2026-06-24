from django.db import models
from django import forms


class RelatedIDField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if add or not value:
            model = model_instance._meta.model
            last_pk = model.objects.filter(user=model_instance.user).aggregate(
                models.Max("related_id", default=0)
            )
            pk = (
                last_pk["related_id__max"] + 1
                if last_pk["related_id__max"] is not None
                else 1
            )
            setattr(model_instance, self.attname, pk)
        return super().pre_save(model_instance, add)


def get_path(instance, filename: str):
    return f"user_{instance.user.id}/{filename}"


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"class": "upload"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
