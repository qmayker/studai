from django.urls import path, include
from .views import ChatListView, ChatDetailView

app_name = "chat"

urlpatterns = [
    path("", ChatListView.as_view(), name="list"),
    path("<int:pk>/", ChatDetailView.as_view(), name="detail"),
]
