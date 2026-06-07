from django.views.generic import DetailView, ListView
from logging import getLogger
from .services.test_result import TestResultServices
from .mixins import ResultViewMixin

# Create your views here.

logger = getLogger(__name__)


class ResultDetailView(ResultViewMixin, DetailView):
    template_name = "quizess/test/detail.html"

    def get_context_data(self, **kwargs):
        service = TestResultServices(result=self.object)
        context_data = super().get_context_data(**kwargs)
        context_data["object_list"] = service.get_answers()
        return context_data


class ResultListView(ResultViewMixin, ListView):
    template_name = "quizess/test/list.html"
