from django.db.models import TextChoices


class Status(TextChoices):
    PENDING = "PN"
    PROCESSING = "PR"
    FINISHED = "FN"
    FAILED = "FL"
