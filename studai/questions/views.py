from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic import View
from django.contrib.auth.mixins import AccessMixin
from django.db.models import QuerySet, F
from logging import getLogger
from chat.models import Chat
from quizess.services.test_attempt import TestAtemptServices
from quizess.services.question_attempt import QuestionAttemptServices
from quizess.services import test_result, answer
from quizess.models import QuestionAttempt
from .forms import AnswerForm
from .services.sessions import QuestionSessionServices
from .services.question import QuestionServices
from .models import Question

# Create your views here.

logger = getLogger(__name__)


class ChatQuestionView(AccessMixin, View):
    model = Question
    template = "questions/question/detail.html"
    end_template = "questions/question/end.html"

    def get_queryset(self, chat_related_id: int):
        qs = self.model.objects.all()
        return qs.filter(chat__related_id=chat_related_id, chat__user=self.request.user)

    def get_form(self, **kwargs):
        return AnswerForm(logger=logger, question_service=self.service, **kwargs)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        chat_related_id = kwargs.get("chat_related_id")
        self._set_db_related(chat_related_id)
        self.session = QuestionSessionServices(
            request.session, chat_rel_id=chat_related_id, logger=logger
        )
        self.attempt_service = self._get_attempt_service(request=request)
        self.question_attempt_service = QuestionAttemptServices(
            attempt=self.attempt_service.attempt
        )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, chat_related_id: int):
        if self.session.has_ended:
            result = test_result.TestResultServices.get_by_attempt_id(
                self.session.attempt_id, user=request.user
            )
            self.session.clear()
            return self.render_end_response(object_list=result.get_answers())
        if not self.session.active:
            self._set_session_active()
            end = self._set_service()
            if end:
                return self.render_end_response(object_list=[])
            self._save_new_page()
        else:
            self._set_attempt_service(
                current_attempt_id=self.session.current_attempt_id
            )
            logger.info(f"{self.service}")

        form = self.get_form()
        return self.render_response(form=form)

    def post(self, request: HttpRequest, chat_related_id: int):
        if not self.session.active:
            raise Http404("Session does not exist")
        if test_result.TestResultServices.exists(
            self.session.attempt_id, self.request.user
        ):
            result = test_result.TestResultServices.get_by_attempt_id(
                self.session.attempt_id, user=request.user
            )
            return self.render_end_response(object_list=result.get_answers())
        self._set_attempt_service(current_attempt_id=self.session.current_attempt_id)
        form = self.get_form(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            self.question_attempt_service.set_answer(
                self.session.current_attempt_id, answer=cd["answer"]
            )
            if self.session.end:
                return self.end_test()
            end = self.next_page()
            if end:
                return self.end_test()
            self._save_new_page()
            form = self.get_form()
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

    def render_end_response(self, object_list: QuerySet[QuestionAttempt]):
        return render(
            self.request, self.end_template, context={"object_list": object_list}
        )

    def _set_service(self) -> bool:
        """Gets current question, creates QuestionService"""
        try:
            self.question: Question = QuestionServices.get_question(
                self.queryset, self.session.current_question_id
            )
            self.service = self.question.question_obj
        except Question.DoesNotExist:
            self.session.delete_question(self.session.current_question_id)
            if not self.session.end:
                return self._set_service()
            return True
        except IndexError:
            return True
        return False

    def _set_attempt_service(self, current_attempt_id: int):
        """Gets QuestionService from current attempt"""
        self.service = QuestionAttempt.objects.get(id=current_attempt_id).question_obj

    def _get_attempt_service(self, request: HttpRequest) -> TestAtemptServices:
        """Get or create TestAttemptServices"""
        if request.method == "GET" and not self.session.active:
            attempt = TestAtemptServices.create(
                chat=self.chat, user=request.user, logger=logger
            )
        else:
            attempt = TestAtemptServices.get(
                chat=self.chat,
                user=request.user,
                id=self.session.attempt_id,
                logger=logger,
            )
        return attempt

    def _create_question_attempt(self, question: Question) -> int:
        """Creates new QuestionAttempt, returns id"""
        q_attempt = self.question_attempt_service.create_question(question=question)
        return q_attempt.id

    def _set_session_active(self):
        """Gets random list of question ids, saves it to session"""
        questions = QuestionServices.get_random_question_ids(
            qs=self.queryset,
        )
        self.session.start_session(questions=questions)
        self._set_service()
        self.session.set_attempt_id(self.attempt_service.attempt.id)

    def _set_db_related(self, chat_related_id: int):
        """Gets chat object and queryset"""
        self.chat = get_object_or_404(
            Chat, related_id=chat_related_id, user=self.request.user
        )
        self.queryset = self.get_queryset(chat_related_id=chat_related_id)

    def next_page(self) -> bool:
        """Increase current_index by 1, get question"""
        self.session.next_page()
        return self._set_service()

    def end_test(self):
        # TODO
        """Ends test"""
        object_list = self.attempt_service.get_result(set(self.session.attempts))
        self.session.set_end()
        result = test_result.TestResultServices.create(
            self.attempt_service.attempt, user=self.request.user
        )
        result.save_answers(object_list)
        return self.render_end_response(object_list=object_list)

    def _save_new_page(self):
        """Creates QuestionAttempt and saves id to session"""
        current_attempt_id = self._create_question_attempt(question=self.question)
        self.session.set_current_attempt(current_attempt_id)
