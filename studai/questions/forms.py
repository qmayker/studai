from logging import Logger
from django.forms import Form, ChoiceField, RadioSelect
from .services.question import QuestionServices


class AnswerForm(Form):
    question = ChoiceField(widget=RadioSelect)

    def __init__(
        self, *args, logger: Logger, question_service: QuestionServices = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        question_field = self.fields["question"]
        question_field.choices = question_service.choices
        question_field.label = question_service.question_name
