from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.db.models import QuerySet
from logging import getLogger
from quizess.services.quizz import QuizzServices
from quizess.services.test_attempt import TestAtemptServices
from quizess.services.question_attempt import QuestionAttemptServices
from quizess.models import TestAtempt
from questions.services.question import QuestionServices
from questions.forms import AnswerForm
from chat.models import Chat
from questions.services.sessions import QuestionSessionServices
from .serializers import AnswerSerializer

logger = getLogger(__name__)


class AnswerView(APIView):
    authentication_classes = [SessionAuthentication]
    serializer = AnswerSerializer

    def get_owned_queryset(self, model):
        return model.objects.filter(user=self.request.user)

    def serialize_answer(self, data, chat_qs: QuerySet, attempt_qs: QuerySet) -> dict:
        answer_serializer = AnswerSerializer(
            data=data, chat_qs=chat_qs, attempt_qs=attempt_qs
        )
        answer_serializer.is_valid(raise_exception=True)
        return answer_serializer.validated_data

    def post(self, request: Request, format=None):
        validated_data = self.serialize_answer(
            data=request.POST,
            chat_qs=self.get_owned_queryset(model=Chat),
            attempt_qs=self.get_owned_queryset(model=TestAtempt),
        )
        attempt: TestAtempt = validated_data["attempt"]
        answer: str = validated_data["answer"]
        logger.info(f"Order {attempt.order}")
        test_attempt_service = TestAtemptServices(attempt_id=attempt.id)
        question_attempt_service = QuestionAttemptServices(attemp_id=attempt.id)
        quizz_service = QuizzServices(qa_service=question_attempt_service)
        question_attempt_service.set_answer(
            qs=question_attempt_service.get_queryset(),
            order=attempt.order-1,
            answer=answer,
        )
        res = quizz_service.get(user=request.user, order_id=attempt.order)
        logger.info(f"{res.end}")
        if res.end:
            return self._redirect(url=res.result)
        test_attempt_service.next_order()
        service: QuestionServices = res.result
        form = AnswerForm(question_service=service, attempt_id=attempt.id)
        return Response({"form": form.as_p()})

    @staticmethod
    def _redirect(url: str):
        return Response({"redirect": url})
