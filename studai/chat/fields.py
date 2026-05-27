from django.db import models

class ChatNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            setattr(model_instance, self.attname, f"Chat")
        print(f"name value: {value}")
        return super().pre_save(model_instance, add)
    
class RelatedIDField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if add or not value:
            model = model_instance._meta.model 
            last_pk = model.objects.filter(user=model_instance.user).aggregate(models.Max("related_id", default=0))
            pk = last_pk["related_id__max"] + 1 if last_pk["related_id__max"] is not None else 1
            setattr(model_instance, self.attname, pk) 
        return super().pre_save(model_instance, add)