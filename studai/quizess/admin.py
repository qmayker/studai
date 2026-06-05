from django.contrib import admin
from .models import QuestionAttempt, TestAtempt

# Register your models here.


class QuestionAttemptInline(admin.TabularInline):
    classes = ["collapse"]
    model = QuestionAttempt
    extra = 0

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(TestAtempt)
class TestAtemptAdmin(admin.ModelAdmin):
    list_display = ["user", "chat"]
    inlines = [QuestionAttemptInline]
