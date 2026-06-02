from django.urls import path
from django.conf import settings
from .views import ChatListView, ChatDetailView, ChatQuestionView

app_name = "chat"

urlpatterns = [
    path("", ChatListView.as_view(), name="list"),
    path("<int:pk>/", ChatDetailView.as_view(), name="detail"),
    path("<int:pk>/questions/", ChatQuestionView.as_view(), name="questions"),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
