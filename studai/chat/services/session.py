from django.contrib.sessions.backends.base import SessionBase


class SessionServices:
    NAMESPACE = "chat"

    def __init__(self, session: SessionBase):
        self.session = session
        if not self.session.get(self.NAMESPACE):
            self.session[self.NAMESPACE] = {}

    @property
    def active(self):
        session = self.session_data
        if not session:
            return False
        if self.current_index is None:
            return False
        if self.questions is None:
            return False
        if self.current_index+1 >= len(self.questions):
            return False
        return True

    @property
    def current_index(self):
        return self.session_data.get("current_question_index")

    @property
    def session_data(self):
        return self.session[self.NAMESPACE]
    
    @property
    def questions(self):
        return self.session_data.get("questions")

    def set_questions(self, questions: list[int]):
        self.session_data["questions"] = questions
        self.session.modified = True

    def set_index(self, question_index: int):
        self.session_data["current_question_index"] = question_index
        self.session.modified = True
