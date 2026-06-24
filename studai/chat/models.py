from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from core.fields import RelatedIDField, get_path

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
        indexes = [
            models.Index(fields=["created"]),
            models.Index(fields=["related_id", "user"]),
        ]

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("chat:detail", kwargs={"pk": self.related_id})

    @property
    def chat_name(self):
        if self.name:
            return self.name
        return f"Chat {self.related_id}"


class Content(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="contents")
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def get_content(self):
        return self.content_object.get_content()


class ItemBase(models.Model):
    content = GenericRelation(Content, related_query_name="items")
    created = models.DateTimeField(auto_now_add=True)

    def get_content(self): ...

    class Meta:
        abstract = True


class TextItem(ItemBase):
    text_content = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="texts"
    )

    def get_content(self):
        return self.text_content


class ImageItem(ItemBase):
    image_content = models.ImageField(upload_to=get_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="images"
    )
    description = models.TextField()

    def get_content(self):
        return self.image_content
