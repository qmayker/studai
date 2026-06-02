from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Chat, Content, TextItem, Question

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


class QuestionInline(admin.TabularInline):
    model = Question
    classes = ["collapse"]
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


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


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "question_text", "created")
    list_filter = ("created",)
    search_fields = ("question_text",)
