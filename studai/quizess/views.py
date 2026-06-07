from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, View
from logging import getLogger
from .services.test_result import TestResultServices
from .models import TestResult

# Create your views here.

logger = getLogger(__name__)


class ResultViewMixin(LoginRequiredMixin):
    model = TestResult

    def get_queryset(self: View):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class ResultDetailView(ResultViewMixin, DetailView):
    template_name = "quizess/test/detail.html"

    def get_context_data(self, **kwargs):
        service = TestResultServices(result=self.object)
        context_data = super().get_context_data(**kwargs)
        context_data["object_list"] = service.get_answers()
        return context_data


class ResultListView(ResultViewMixin, ListView):
    template_name = "quizess/test/list.html"
