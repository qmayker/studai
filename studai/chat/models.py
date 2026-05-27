from django.db import models
from django.conf import settings
from .fields import RelatedIDField

# Create your models here.


class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True)
    related_id = RelatedIDField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["created"])]

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("chat:detail", kwargs={"pk": self.related_id})

    @property
    def chat_name(self):
        if self.name:
            return self.name
        return f"Chat {self.related_id}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
