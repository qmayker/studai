from typing import NamedTuple
from quizess.models import QuestionAttempt


class TestResult(NamedTuple):
    correct: list[QuestionAttempt]
    wrong: list[QuestionAttempt]
