from rest_framework.routers import SimpleRouter
from .views import ChatViewSet

router = SimpleRouter()
router.register("chat", ChatViewSet, basename="chat")

app_name = "chat_api"
urlpatterns = []
urlpatterns += router.urls
