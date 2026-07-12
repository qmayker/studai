from django.db import models
from django.conf import settings
from core.fields import RelatedIDField

# Create your models here.


class UserSocket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sockets"
    )
    socket_id = models.CharField()
    related_id = RelatedIDField()