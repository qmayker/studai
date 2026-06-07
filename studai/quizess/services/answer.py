from django.db.models import QuerySet
from quizess.models import QuestionAttempt, Answer, TestResult


class AnswerServices:
    def __init__(self, result: TestResult):
        self.result = result

    def save_answers(self, questions: QuerySet[QuestionAttempt]):
        answers = []
        for question in questions:
            answers.append(
                Answer(
                    question=question,
                    result=self.result,
                    correct=question.correct,
                    answer=question.answer,
                )
            )
        Answer.objects.bulk_create(objs=answers)
