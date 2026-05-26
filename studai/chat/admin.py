from django.contrib import admin
from .models import Chat, Message

# Register your models here.

class MessageInline(admin.StackedInline):
    model = Message
    classes = ["collapse"]
    extra = 0

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created")
    list_filter = ("created",)
    search_fields = ("user__username",)
    inlines = [MessageInline]
