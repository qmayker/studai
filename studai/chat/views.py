from django.shortcuts import render
from django.views.generic import ListView
from .models import Chat

# Create your views here.


class ChatListView(ListView):
    model = Chat
    template_name = "chat/chat/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
