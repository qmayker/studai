from logging import getLogger
from django.forms import Form, ChoiceField, RadioSelect, BooleanField, HiddenInput
from .services.question import QuestionServices

logger = getLogger(__name__)


class AnswerForm(Form):
    answer = ChoiceField(widget=RadioSelect, required=True)

    def __init__(
        self,
        *args,
        question_service: QuestionServices,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        answer_field = self.fields["answer"]
        answer_field.choices = question_service.choices
        answer_field.label = question_service.question_name
