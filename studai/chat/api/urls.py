from django.urls import path

from .views import SaveContentApi

app_name = "chat_api"
urlpatterns = [path("save_content/", SaveContentApi.as_view(), name="save_content")]
