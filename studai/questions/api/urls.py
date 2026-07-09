from django.urls import path
from .views import AnswerView

app_name = "questions_api"
urlpatterns = [path("answer/", AnswerView.as_view(), name="answer")]
