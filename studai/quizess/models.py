from django.db import models
from django.conf import settings
from questions.services.question import QuestionServices
from .querysets import QuestionAttemptQueryset
from core.fields import RelatedIDField

# Create your models here.

# TODO related_id, names


class TestAtempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts"
    )
    chat = models.ForeignKey(
        "chat.Chat", on_delete=models.CASCADE, related_name="attempts"
    )
    related_id = RelatedIDField()


class QuestionAttempt(models.Model):
    attempt = models.ForeignKey(
        TestAtempt, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer_letter = models.CharField(max_length=1)
    created = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=1, null=True)
    objects = QuestionAttemptQueryset.as_manager()

    @property
    def question_obj(self):
        return QuestionServices(
            options=self.options,
            question_name=self.question_text,
            correct_answer_letter=self.correct_answer_letter,
        )

    @property
    def correct(self):
        return self.answer == self.correct_answer_letter


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
