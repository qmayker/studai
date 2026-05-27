from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Chat
from .forms import TextContentForm

# Create your views here.


class ChatViewMixin:
    model = Chat

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ChatListView(LoginRequiredMixin, ChatViewMixin, ListView):
    template_name = "chat/chat/list.html"


class ChatDetailView(LoginRequiredMixin, ChatViewMixin, DetailView):
    template_name = "chat/chat/detail.html"

    def _get_message_form(self):
        return TextContentForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self.object.messages.all()
        context["form"] = self._get_message_form()
        return context

    def get_object(self, queryset=None):
        qs = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(qs, related_id=pk, user=self.request.user)
        return obj
