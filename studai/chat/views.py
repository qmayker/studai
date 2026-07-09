from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from logging import getLogger
from .models import Chat
from .forms import TextContentForm, ImageContentForm

# Create your views here.

logger = getLogger(__name__)


class RelatedIDChatViewMixin:
    model = Chat

    def get_object(self, queryset=None):
        qs = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(qs, related_id=pk)
        return obj

    def validate_exists(self, queryset=None):
        qs = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not qs.filter(related_id=pk).exists():
            raise Http404("Chat does not exist")

    def get_queryset(self):
        qs = self.model.objects.filter(user=self.request.user)
        return qs


class ChatListView(LoginRequiredMixin, RelatedIDChatViewMixin, ListView):
    template_name = "chat/chat/list.html"


class ChatDetailView(LoginRequiredMixin, RelatedIDChatViewMixin, DetailView):
    template_name = "chat/chat/detail.html"
    image_form = ImageContentForm
    text_form = TextContentForm

    def _get_text_form(self):
        return self.text_form()

    def _get_image_form(self):
        return self.image_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contents"] = self.object.contents.all()
        context["form"] = self._get_text_form()
        context["image_form"] = self._get_image_form()
        return context
