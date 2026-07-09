from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.db.models import QuerySet
from logging import getLogger
from quizess.services.quizz import QuizzServices
from quizess.services.question_attempt import QuestionAttemptServices
from questions.services.question import QuestionServices
from questions.forms import AnswerForm
from chat.models import Chat
from questions.services.sessions import QuestionSessionServices
from .serializers import AnswerSerializer

logger = getLogger(__name__)


class AnswerView(APIView):
    authentication_classes = [SessionAuthentication]
    serializer = AnswerSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)

    def serialize_answer(self, data, qs: QuerySet) -> dict:
        answer_serializer = AnswerSerializer(data=data, qs=qs)
        answer_serializer.is_valid(raise_exception=True)
        return answer_serializer.validated_data

    def post(self, request: Request, format=None):
        validated_data = self.serialize_answer(
            data=request.POST, qs=self.get_queryset()
        )
        chat: Chat = validated_data["chat"]
        questions = chat.questions.all()
        answer: str = validated_data["answer"]

        session = QuestionSessionServices(
            session=self.request.session, chat_rel_id=chat.related_id
        )
        quizz_service = QuizzServices(session=session)
        question_attempt_service = QuestionAttemptServices(attemp_id=session.attempt_id)

        question_attempt_service.set_answer(
            qs=question_attempt_service.get_queryset(),
            id=session.current_question_attempt_id,
            answer=answer,
        )
        if session.last_id:
            result_service = quizz_service.save_quizz_result(user=request.user)
            return self._redirect(url=result_service.result_url)
        session.next_page()
        res = quizz_service.get(
            qs=questions,
            question_attempt_service=question_attempt_service,
            user=request.user,
        )
        if res.end:
            return self._redirect(url=res.result)
        service: QuestionServices = res.result
        form = AnswerForm(question_service=service)
        return Response({"form": form.as_p()})

    @staticmethod
    def _redirect(url: str):
        return Response({"redirect": url})
