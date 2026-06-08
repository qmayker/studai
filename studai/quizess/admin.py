from django.contrib import admin
from .models import QuestionAttempt, TestAtempt, TestResult, Answer
from .mixins import NonEditableInlineMixin

# Register your models here.


class QuestionAttemptInline(NonEditableInlineMixin, admin.TabularInline):
    model = QuestionAttempt


class AnswerInline(NonEditableInlineMixin, admin.TabularInline):
    model = Answer


@admin.register(TestAtempt)
class TestAtemptAdmin(admin.ModelAdmin):
    list_display = ["user", "chat"]
    inlines = [QuestionAttemptInline]
    readonly_fields = ("related_id",)


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ["user"]
    inlines = [AnswerInline]
