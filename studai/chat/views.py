import random
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from logging import getLogger
from questions.models import Question
from .services.session import SessionServices
from .models import Chat
from .forms import TextContentForm

# Create your views here.

logger = getLogger(__name__)


class RelatedIDChatViewMixin:
    model = Chat

    def get_object(self, queryset=None):
        qs = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(qs, related_id=pk)
        return obj

    def validate_exists(self, queryset=None):
        qs = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not qs.filter(related_id=pk).exists():
            raise Http404("Chat does not exist")

    def get_queryset(self):
        qs = self.model.objects.filter(user=self.request.user)
        return qs


class ChatListView(LoginRequiredMixin, RelatedIDChatViewMixin, ListView):
    template_name = "chat/chat/list.html"


class ChatDetailView(LoginRequiredMixin, RelatedIDChatViewMixin, DetailView):
    template_name = "chat/chat/detail.html"

    def _get_message_form(self):
        return TextContentForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contents"] = self.object.contents.all()
        context["form"] = self._get_message_form()
        return context


class ChatQuestionView(LoginRequiredMixin, RelatedIDChatViewMixin, DetailView):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.session = SessionServices(request.session)
        return super().dispatch(request, *args, **kwargs)

    def generate_random_questions(self):
        question_ids = list(
            Question.objects.filter(chat=self.object).values_list("id", flat=True)
        )
        random.shuffle(question_ids)
        return question_ids

    def get(self, request: HttpRequest, pk: int):
        self.object = self.get_object()
        if not self.session.active:
            questions = self.generate_random_questions()
            index = 0
            self.session.set_questions(questions)
            self.session.set_index(index)
        else:
            index = self.session.current_index
            questions = self.session.questions

        question_id = questions[index]
        question = get_object_or_404(Question, id=question_id)
        logger.info(
            f"Question {question} is served for chat {self.object.id} at index {index}"
        )
        return HttpResponse(f"Question: {question.question_text}, Options: {question.options}")
        # TODO
