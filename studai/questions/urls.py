from django.urls import path
from .views import ChatQuestionView

app_name = "questions"

urlpatterns = [
    path("<int:chat_id>/", ChatQuestionView.as_view(), name="questions"),
]
