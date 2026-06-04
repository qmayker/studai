from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from chat.models import Chat
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
        chat_related_id = kwargs.get("chat_related_id")
        self.chat = get_object_or_404(
            Chat, related_id=chat_related_id, user=self.request.user
        )
        self.queryset = self.get_queryset(chat_related_id=chat_related_id)
        self.session = QuestionSessionServices(
            request.session, chat_rel_id=chat_related_id
        )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, chat_related_id: int):
        if not self.session.active:
            questions = QuestionServices.generate_random_questions_id(
                chat_related_id=chat_related_id,
                qs=self.get_queryset(chat_related_id=chat_related_id),
            )
            self.session.start_session(questions=questions)
        self.service = QuestionServices.get_service(
            self.queryset, self.session.current_question_id
        )
        form = self.get_form()
        return self.render_response(form=form)

    def post(self, request: HttpRequest, chat_related_id: int):
        self.service = QuestionServices.get_service(
            self.queryset, self.session.current_question_id
        )
        form = self.get_form(
            data=request.POST
        )
        if not form.is_valid():
            return self.render_response(form=form)
        cd = form.cleaned_data
        self.session.set_answer(answer_letter=cd["answer"])
        if self.session.end:
            self.session.end_session(qs=self.queryset)
            return
        self.session.next_page()
        form = self.get_form()
        return self.render_response(form=form)

        logger.info(f"{self.session.end_session(end=cd['end'], qs=self.queryset)}")

        return HttpResponse("ok")

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
