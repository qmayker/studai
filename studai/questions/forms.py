from django.forms import Form, ChoiceField
from .services.question import QuestionServices


class AnswerForm(Form):
    answer = ChoiceField(label="")

    def __init__(self, *args, question: QuestionServices = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["answer"].choices = [
            (letter, letter) for letter in question.option_letters
        ]
