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
    attempt = models.ForeignKey(
        TestAtempt, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer_letter = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=1, null=True)
