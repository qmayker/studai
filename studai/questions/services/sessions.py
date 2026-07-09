from django.contrib.sessions.backends.base import SessionBase
from logging import getLogger
from core.decorators import modifying

logger = getLogger(__name__)


class QuestionSessionServices:
    NAMESPACE = "question"

    def __init__(self, session: SessionBase, chat_rel_id: int):
        self.chat_rel_id = str(chat_rel_id)
        self._session = session
        session_data = self.get_session()

        if not session_data:
            self.session = self._create(session=self._session, namespace=self.NAMESPACE)
        else:
            self.session = session_data
        self.chat_session = self.get_chat_session(session=self.session)

    @property
    def chat_namespace(self):
        return f"chat_{self.chat_rel_id}"

    @property
    def active(self):
        return self.chat_session is not None

    @property
    def current_index(self) -> int:
        return self.chat_session["index"]

    @property
    def current_id(self) -> int:
        return self.ids[self.current_index]

    @property
    def last_id(self):
        if len(self.ids) == self.current_index + 1:
            return True
        return False

    @property
    def _ids(self) -> dict[str, None | int]:
        return self.chat_session["ids"]

    @property
    def ids(self) -> tuple[str]:
        return tuple(self._ids.keys())

    @property
    def attempt_ids(self) -> tuple[str]:
        return tuple(self._ids.values())

    @property
    def attempt_id(self) -> int:
        return self.chat_session["attempt_id"]

    @property
    def current_question_attempt_id(self) -> int | None:
        return int(self._ids[self.current_id])

    def get_question_attempt_id(self, question_id: int) -> int | None:
        return self._ids[str(question_id)]

    def get_session(self) -> dict | None:
        data = self._session.get(self.NAMESPACE)
        return data

    def get_chat_session(self, session: dict) -> None | dict:
        data = session.get(self.chat_namespace)
        return data

    @modifying
    def _create(self, session: dict, namespace: str):
        session[namespace] = {}
        return session[namespace]

    @modifying
    def clear(self):
        chat_data = self.session.pop(self.chat_namespace)
        self.chat_session = None
        return chat_data

    def start(self, questions: list[int], attempt_id: int):
        self.chat_session = self._create(
            session=self.session, namespace=self.chat_namespace
        )
        self.set_question_related(questions=questions)
        self.set_attempt_related(attempt_id=attempt_id)

    @modifying
    def _save_ids(self, chat: dict, questions: list[int]):
        ids = {}
        for question in questions:
            ids[str(question)] = None
        chat["ids"] = ids

    @modifying
    def set_index(self, index: int):
        self.chat_session["index"] = index

    @modifying
    def _set_attempt_id(self, attempt_id: int):
        self.chat_session["attempt_id"] = attempt_id

    @modifying
    def delete_id(self, question_id: int):
        self._ids.pop(question_id)

    def set_attempt_related(self, attempt_id: int):
        self._set_attempt_id(attempt_id=attempt_id)

    def set_question_related(self, questions: list[int]):
        self._save_ids(chat=self.chat_session, questions=questions)
        self.set_index(0)

    @modifying
    def add_question_attempt(self, question_attempt_id: int):
        self._ids[self.current_id] = question_attempt_id

    @modifying
    def next_page(self) -> int:
        new_index = self.current_index + 1
        self.set_index(new_index)
        return new_index
