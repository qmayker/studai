from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Chat

# Create your views here.


class ChatViewMixin:
    model = Chat

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class ChatListView(ChatViewMixin, ListView):
    template_name = "chat/chat/list.html"


class ChatDetailView(ChatViewMixin, DetailView):
    template_name = "chat/chat/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self.object.messages.all()
        return context
