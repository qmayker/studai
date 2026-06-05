from django.contrib.sessions.backends.base import SessionBase
from django.db.models import F
from logging import Logger
from functools import wraps
from typing import NamedTuple
from quizess.models import QuestionAttempt


def modifying(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._session.modified = True
        return result

    return wrapper


class TestResult(NamedTuple):
    correct: list[int]
    wrong: list[int]


class QuestionSessionServices:
    NAMESPACE = "question"

    # TODO - chat_id namespace
    def __init__(self, session: SessionBase, chat_rel_id: int, logger: Logger):
        self._session = session
        self.chat_rel_id = str(chat_rel_id)
        self.logger = logger
        if not self._session.get(self.NAMESPACE):
            self._session[self.NAMESPACE] = {}
        if not self._session[self.NAMESPACE].get(self.chat_namespace):
            self._session[self.NAMESPACE][self.chat_namespace] = {}

    @property
    def active(self):
        session = self.session_data
        if not session:
            return False
        if self.current_index is None:
            return False
        if self.questions is None:
            return False
        if self.current_index >= len(self.questions):
            return False
        return True

    @property
    def chat_namespace(self):
        return f"chat_{self.chat_rel_id}"

    @property
    def current_index(self):
        return self.session_data.get("current_question_index")

    @property
    def session_data(self):
        return self._session[self.NAMESPACE][self.chat_namespace]

    @property
    def questions(self) -> list[int]:
        return self.session_data.get("questions")

    @property
    def end(self):
        if self.current_index + 1 == len(self.questions):
            return True
        return False

    @property
    def current_question_id(self):
        return self.questions[self.current_index]

    @property
    def attempts(self) -> dict:
        if self.session_data.get("attempts") is None:
            self._create_attempts()
        return self.session_data["attempts"]

    @property
    def attempt_id(self) -> int:
        return self.session_data["attempt"]

    @property
    def current_question_attempt_id(self) -> int:
        return self.attempts[str(self.current_question_id)]

    @property
    def question_attempt_ids(self) -> set[int]:
        return set(self.attempts.values())

    @property
    def has_ended(self) -> bool:
        return self.session_data.get("ended", False)

    @modifying
    def set_questions(self, questions: list[int]):
        self.session_data["questions"] = questions

    @modifying
    def set_index(self, question_index: int):
        self.session_data["current_question_index"] = question_index

    def clear(self):
        self._session.pop(self.NAMESPACE, None)

    def start_session(self, questions: list):
        self.set_questions(questions)
        self.set_index(0)

    def _end(self) -> TestResult:
        questions = self.question_attempt_ids
        correct_answers = set(
            QuestionAttempt.objects.filter(
                id__in=questions, answer=F("correct_answer_letter")
            ).values_list("id", flat=True)
        )
        wrong_answers = questions - correct_answers
        return TestResult(correct=correct_answers, wrong=wrong_answers)

    def end_session(self) -> TestResult:
        r = self._end()
        self.clear()
        return r

    def next_page(self):
        new_index = self.current_index + 1
        self.set_index(new_index)
        return new_index

    @modifying
    def set_attempt_id(self, attempt_id: int):
        self.session_data["attempt"] = attempt_id

    @modifying
    def set_question_attempt_id(self, question_attempt_id: int):
        self.attempts[str(self.current_question_id)] = question_attempt_id

    @modifying
    def _create_attempts(self):
        self.session_data["attempts"] = {}

    @modifying
    def set_end(self):
        self.session_data["ended"] = True

    @modifying
    def delete_question(self, question_id:int):
        self.questions.remove(question_id)
