from logging import Logger
from django.forms import Form, ChoiceField, RadioSelect, BooleanField, HiddenInput
from .services.question import QuestionServices


class AnswerForm(Form):
    answer = ChoiceField(widget=RadioSelect)
    end = BooleanField(widget=HiddenInput)

    def __init__(
        self, *args, logger: Logger, question_service: QuestionServices = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        answer_field = self.fields["answer"]
        answer_field.choices = question_service.choices
        answer_field.label = question_service.question_name
