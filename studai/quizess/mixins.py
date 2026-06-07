from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import TestResult


class NonEditableInlineMixin:
    classes = ["collapse"]
    extra = 0
    max_num = 1

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


class ResultViewMixin(LoginRequiredMixin):
    model = TestResult

    def get_queryset(self: View):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
