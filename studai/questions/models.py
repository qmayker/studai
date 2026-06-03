from logging import getLogger

from django.db import models

from chat.models import Chat
from .services.question import QuestionServices

# Create your models here.

logger = getLogger(__name__)


class Question(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer_letter = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def question_obj(self):
        return QuestionServices(
            options=self.options,
            question_name=self.question_text,
            correct_answer_letter=self.correct_answer_letter,
        )

    def __str__(self):
        return f"{self.question_text}"
