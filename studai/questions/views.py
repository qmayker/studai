from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import AccessMixin
from django.forms import Form
from logging import getLogger
from chat.models import Chat
from quizess.services.test_attempt import TestAtemptServices
from quizess.services.question_attempt import QuestionAttemptServices
from quizess.services.quizz import QuizzServices
from .forms import AnswerForm
from .services.sessions import QuestionSessionServices
from .services.question import QuestionServices
from .models import Question

# Create your views here.

logger = getLogger(__name__)


class ChatQuestionView(AccessMixin, View):
    model = Question
    template = "questions/question/detail.html"
    end_template = "quizess/test/detail.html"

    def get_form(self, service: QuestionServices, **kwargs):
        return AnswerForm(question_service=service, **kwargs)

    def get_chat(self, chat_related_id: int):
        return Chat.objects.get(related_id=chat_related_id, user=self.request.user)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()

        chat_related_id = kwargs.get("chat_related_id")
        self.chat = self.get_chat(chat_related_id=chat_related_id)
        self.questions = self.chat.questions.all()

        self.session = QuestionSessionServices(
            session=request.session, chat_rel_id=chat_related_id
        )
        self.quizz_service = QuizzServices(session=self.session)

        self.attempt_service = self.get_attempt_service(request=request, chat=self.chat)
        self.question_attempt_service = QuestionAttemptServices(
            attemp_id=self.attempt_service.attempt.id,
        )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, chat_related_id: int):
        self.quizz_service.check_session(
            qs=self.questions, attempt_id=self.attempt_service.attempt.id
        )

        result = self.quizz_service.get(
            qs=self.questions,
            user=request.user,
            question_attempt_service=self.question_attempt_service,
        )
        if result.end:
            return self.render_end_response(result.result)
        service: QuestionServices = result.result

        form = self.get_form(service=service)
        return self.render_response(
            form=form, service=service, chat_related_id=chat_related_id
        )

    def get_context_data(self, service, form):
        context = {"service": service, "form": form}
        return context

    def render_response(self, form: Form, service: QuestionServices, **kwargs):
        context = self.get_context_data(service=service, form=form)
        context.update(kwargs)
        return render(
            self.request,
            self.template,
            context=context,
        )

    def render_end_response(self, url: str):
        return redirect(url)

    def get_attempt_service(
        self, request: HttpRequest, chat: Chat
    ) -> TestAtemptServices:
        """Get or create TestAttemptServices"""
        if request.method == "GET" and not self.session.active:
            attempt = TestAtemptServices.create(chat=chat, user=request.user)
        else:
            attempt = TestAtemptServices.get(
                chat=self.chat,
                user=request.user,
                id=self.session.attempt_id,
            )
        return attempt
