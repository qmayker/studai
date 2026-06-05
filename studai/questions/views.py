from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from chat.models import Chat
from quizess.services.test_attempt import TestAtemptServices
from quizess.services.question_attempt import QuestionAttemptServices
from .forms import AnswerForm
from .services.sessions import QuestionSessionServices
from .services.question import QuestionServices
from .models import Question

# Create your views here.

logger = getLogger(__name__)


class ChatQuestionView(LoginRequiredMixin, View):
    model = Question
    template = "questions/detail.html"

    def get_queryset(self, chat_related_id: int):
        qs = self.model.objects.all()
        return qs.filter(chat__related_id=chat_related_id, chat__user=self.request.user)

    def get_form(self, **kwargs):
        return AnswerForm(logger=logger, question_service=self.service, **kwargs)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # TODO - move logic to other methods
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        chat_related_id = kwargs.get("chat_related_id")
        self._set_db_related(chat_related_id)
        self.session = QuestionSessionServices(
            request.session, chat_rel_id=chat_related_id, logger=logger
        )
        self.testAttemptService = TestAtemptServices(self.chat, self.request.user)
        self._set_service()
        self._set_attempt(request=request, attemptService=self.testAttemptService)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, chat_related_id: int):
        if not self.session.active:
            self._set_session_active()
        self._set_question_attempt(question=self.question)
        form = self.get_form()
        return self.render_response(form=form)

    def post(self, request: HttpRequest, chat_related_id: int):
        # TODO - if handle error if session doesnt exist
        # TODO - handle error if new question does not exist
        form = self.get_form(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            self.questionAttemptService.set_answer(
                self.session.current_question_attempt_id, answer=cd["answer"]
            )
            if self.session.end:
                res = self.session.end_session()
                logger.info(f"{res}")
                return HttpResponse("end")
            self.session.next_page()
            self._set_service()
            self._set_question_attempt(question=self.question)
            form = self.get_form()
            return self.render_response(form=form)
        return self.render_response(form=form)

    def get_context_data(self, service, end: bool, **kwargs):
        context = {"service": service, "end": end}
        context.update(**kwargs)
        return context

    def render_response(self, **kwargs):
        return render(
            self.request,
            self.template,
            context=self.get_context_data(self.service, self.session.end, **kwargs),
        )

    def _set_service(self):
        if not self.session.active:
            return
        self.question: Question = QuestionServices.get_question(
            self.queryset, self.session.current_question_id
        )
        self.service = self.question.question_obj

    def _set_attempt(self, request: HttpRequest, attemptService: TestAtemptServices):
        if request.method == "GET" and not self.session.active:
            self.attempt = attemptService.create()
        else:
            self.attempt = attemptService.get(self.session.attempt_id)
        self.questionAttemptService = QuestionAttemptServices(attempt=self.attempt)

    def _set_question_attempt(self, question: Question):
        q_attempt = self.questionAttemptService.create_question(question=question)
        self.session.set_question_attempt_id(q_attempt.id)

    def _set_session_active(self):
        questions = QuestionServices.get_random_question_ids(
            qs=self.queryset,
        )
        self.session.start_session(questions=questions)
        self._set_service()
        self.session.set_attempt_id(self.attempt.id)

    def _set_db_related(self, chat_related_id: int):
        self.chat = get_object_or_404(
            Chat, related_id=chat_related_id, user=self.request.user
        )
        self.queryset = self.get_queryset(chat_related_id=chat_related_id)
