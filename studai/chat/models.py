from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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


class Content(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class ItemBase(models.Model):
    content = GenericRelation(Content, related_query_name="items")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TextItem(ItemBase):
    text_content = models.TextField()
