from django.contrib.sessions.backends.base import SessionBase


class QuestionSessionServices:
    NAMESPACE = "question"

    # TODO - chat_id namespace
    def __init__(self, session: SessionBase, chat_rel_id: int):
        self.session = session
        self.chat_rel_id = str(chat_rel_id)
        if not self.session.get(self.NAMESPACE):
            self.session[self.NAMESPACE] = {}
        if not self.session[self.NAMESPACE].get(self.chat_namespace):
            self.session[self.NAMESPACE][self.chat_namespace] = {}

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
        return self.session[self.NAMESPACE][self.chat_namespace]

    @property
    def questions(self):
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
    def answers(self) -> dict:
        if self.session_data.get("answers") is None:
            self.session_data["answers"] = {}
        return self.session_data["answers"]

    def set_questions(self, questions: list[int]):
        self.session_data["questions"] = questions
        self.session.modified = True

    def set_index(self, question_index: int):
        self.session_data["current_question_index"] = question_index
        self.session.modified = True

    def clear(self):
        self.session.pop(self.NAMESPACE, None)

    def start_session(self, questions: list):
        self.set_questions(questions)
        self.set_index(0)

    def set_answer(self, answer_letter: str):
        self.answers[f"q_{self.current_question_id}"] = answer_letter
