from django.db.models import QuerySet
from django.http import Http404
from questions.models import Question
from quizess.models import QuestionAttempt


class QuestionAttemptServices:
    def __init__(self, attemp_id: int):
        self.attempt_id = attemp_id

    def _create_kwargs(self, question: Question) -> dict:
        return {
            "attempt_id": self.attempt_id,
            "question_text": question.question_text,
            "answer": None,
            "options": question.options,
            "correct_answer_letter": question.correct_answer_letter,
        }

    def create_question(self, question: Question) -> QuestionAttempt:
        return QuestionAttempt.objects.create(**self._create_kwargs(question=question))

    def get_queryset(self):
        queryset = QuestionAttempt.objects.filter(attempt_id=self.attempt_id)
        return queryset

    @staticmethod
    def set_answer(qs: QuerySet, id: int, answer: str):
        return qs.filter(id=id).update(answer=answer)

    @staticmethod
    def get_question(qs: QuerySet, id: int) -> QuestionAttempt:
        return qs.get(id=id)

    def get_or_create_question_attempt(
        self, question: Question | None, question_attempt_id: int | None
    ) -> QuestionAttempt:
        if question_attempt_id:
            qs = self.get_queryset()
            question_attempt = self.get_question(qs=qs, id=question_attempt_id)
        elif question:
            question_attempt = self.create_question(question=question)
        else:
            raise Http404()
        return question_attempt
