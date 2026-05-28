from django.urls import path

from .views import SaveContentApi, GenerateQuestionsApi

app_name = "chat_api"
urlpatterns = [
    path("save_content/", SaveContentApi.as_view(), name="save_content"),
    path("generate/", GenerateQuestionsApi.as_view(), name="generate_questions"),
]
