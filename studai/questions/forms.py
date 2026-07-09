from logging import getLogger
from django.forms import Form, ChoiceField, RadioSelect, IntegerField, HiddenInput
from .services.question import QuestionServices

logger = getLogger(__name__)


class AnswerForm(Form):
    answer = ChoiceField(widget=RadioSelect, required=True)
    attempt = IntegerField(widget=HiddenInput, required=True)

    def __init__(
        self,
        *args,
        question_service: QuestionServices,
        attempt_id: int,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        answer_field = self.fields["answer"]
        answer_field.choices = question_service.choices
        answer_field.label = question_service.question_name
        attempt_field = self.fields["attempt"]
        attempt_field.initial = attempt_id
