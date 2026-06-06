from django.contrib.sessions.backends.base import SessionBase

from logging import Logger
from functools import wraps
from typing import NamedTuple



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
        return self.session_data["current_question_index"]

    @property
    def session_data(self) -> dict:
        return self._session.get(self.NAMESPACE, {}).get(self.chat_namespace, {})

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
    def attempt_id(self) -> int:
        return self.session_data["attempt"]

    @property
    def attempts(self) -> list[int]:
        return self.session_data["attempts"]

    @property
    def current_attempt_id(self) -> int | None:
        return self.session_data.get("current_attempt")

    @property
    def has_ended(self) -> bool:
        return self.session_data.get("ended", False)

    @modifying
    def set_questions(self, questions: list[int]):
        self.session_data["questions"] = questions

    @modifying
    def delete_question(self, question_id: int):
        self.questions.remove(question_id)

    @modifying
    def set_index(self, question_index: int):
        self.session_data["current_question_index"] = question_index

    def clear(self):
        self._session.pop(self.NAMESPACE, None)

    def start_session(self, questions: list):
        if not self._session.get(self.NAMESPACE):
            self._session[self.NAMESPACE] = {}
        if not self._session[self.NAMESPACE].get(self.chat_namespace):
            self._session[self.NAMESPACE][self.chat_namespace] = {}
        self.set_questions(questions)
        self._create_attempts()
        self.set_index(0)


    def next_page(self):
        new_index = self.current_index + 1
        self.set_index(new_index)
        return new_index

    @modifying
    def set_attempt_id(self, attempt_id: int):
        self.session_data["attempt"] = attempt_id

    @modifying
    def _create_attempts(self):
        self.session_data["attempts"] = []

    @modifying
    def add_attempt(self, attempt_id: int):
        self.attempts.append(attempt_id)

    @modifying
    def set_end(self):
        self.session_data["ended"] = True

    @modifying
    def set_current_attempt(self, attempt_id: int):
        self.session_data["current_attempt"] = attempt_id
        self.add_attempt(attempt_id=attempt_id)
