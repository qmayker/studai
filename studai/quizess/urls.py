from django.urls import path
from .views import ResultDetailView, ResultListView

app_name = "quizess"

urlpatterns = [
    path("<int:pk>/", ResultDetailView.as_view(), name="detail"),
    path("", ResultListView.as_view(), name="list"),
]
