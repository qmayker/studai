from django.db import models
from django.conf import settings
from questions.services.question import QuestionServices
from .querysets import QuestionAttemptQueryset
from core.fields import RelatedIDField

# Create your models here.


class TestAtempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts"
    )
    chat = models.ForeignKey(
        "chat.Chat", on_delete=models.CASCADE, related_name="attempts"
    )
    related_id = RelatedIDField()
    order = models.PositiveIntegerField(default=0)


class QuestionAttempt(models.Model):
    attempt = models.ForeignKey(
        TestAtempt, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer_letter = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=1, null=True)
    order = models.PositiveIntegerField()
    objects = QuestionAttemptQueryset.as_manager()

    class Meta:
        ordering = ["order"]

    @property
    def service(self) -> QuestionServices:
        return QuestionServices(
            options=self.options,
            question_name=self.question_text,
            correct_answer_letter=self.correct_answer_letter,
        )

    @property
    def correct(self) -> bool:
        return self.answer == self.correct_answer_letter

    @property
    def chat_related_id(self) -> int:
        return self.attempt.chat.related_id


class TestResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="results"
    )
    attempt = models.OneToOneField(
        TestAtempt, on_delete=models.CASCADE, related_name="result"
    )


class Answer(models.Model):
    question = models.OneToOneField(
        QuestionAttempt, on_delete=models.CASCADE, related_name="result"
    )
    result = models.ForeignKey(
        TestResult, on_delete=models.CASCADE, related_name="answers"
    )
    answer = models.CharField(max_length=1, null=True)
    correct = models.BooleanField(default=False)
