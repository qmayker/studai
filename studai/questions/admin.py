from django.contrib import admin
from .models import Question

# Register your models here.


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "question_text", "created")
    list_filter = ("created",)
    search_fields = ("question_text",)


class QuestionInline(admin.TabularInline):
    model = Question
    classes = ["collapse"]
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False
