from django.db import models
from django.conf import settings

# Create your models here.


class TestAtempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempt"
    )
    chat = models.ForeignKey(
        "chat.Chat", on_delete=models.CASCADE, related_name="attempts"
    )


class QuestionAttempt(models.Model):
    question = models.ForeignKey(
        "questions.Question", on_delete=models.CASCADE, related_name="attempts"
    )
    answer = models.CharField(max_length=1)
