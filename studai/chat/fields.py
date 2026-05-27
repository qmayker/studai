from django.db import models

class ChatNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        print(value)
        return super().pre_save(model_instance, add)