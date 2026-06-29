from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from questions.admin import QuestionInline
from .models import Chat, Content, TextItem, ImageItem

# Register your models here.


class ContentGenericInline(GenericTabularInline):
    model = Content
    classes = ["collapse"]
    extra = 0
    max_num = 1


class ContentInline(admin.TabularInline):
    model = Content
    classes = ["collapse"]
    extra = 0


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "content_type", "object_id")
    list_filter = ("content_type",)
    search_fields = ("chat__name",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created", "chat_name")
    list_filter = ("created",)
    search_fields = ("user__username",)
    readonly_fields = ("related_id", "chat_name")
    inlines = [ContentInline, QuestionInline]


@admin.register(TextItem)
class TextAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "text_content")
    list_filter = ("created",)
    search_fields = ("text_content",)
    inlines = [ContentGenericInline]


@admin.register(ImageItem)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "image_content", "status")
    list_filter = ("created", "status")
    inlines = [ContentGenericInline]
