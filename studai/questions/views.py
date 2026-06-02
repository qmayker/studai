import random
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from chat.models import Chat
from .services.sessions import QuestionSessionServices
from .models import Question

# Create your views here.

logger = getLogger(__name__)


class ChatQuestionView(LoginRequiredMixin, View):
    model = Question

    def get_queryset(self, chat_id: int):
        qs = self.model.objects.all()
        return qs.filter(chat_id=chat_id, chat__user=self.request.user)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.session = QuestionSessionServices(request.session)
        return super().dispatch(request, *args, **kwargs)

    def generate_random_questions(self, chat_id: int):
        question_ids = list(
            self.get_queryset(chat_id=chat_id).values_list("id", flat=True)
        )
        random.shuffle(question_ids)
        return question_ids

    def get(self, request: HttpRequest, chat_id: int):
        if not self.session.active:
            questions = self.generate_random_questions(chat_id=chat_id)
            index = 0
            self.session.set_questions(questions)
            self.session.set_index(index)
        else:
            index = self.session.current_index
            questions = self.session.questions

        question_id = questions[index]
        question = get_object_or_404(Question, id=question_id)
        logger.info(
            f"Question {question} is served for chat {chat_id} at index {index}"
        )
        self.session.clear()
        return HttpResponse(
            f"Question: {question.question_text}, Options: {question.options}"
        )
        # TODO
