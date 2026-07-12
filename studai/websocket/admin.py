from django.contrib import admin
from .models import UserSocket

# Register your models here.


@admin.register(UserSocket)
class UserSocketAdmin(admin.ModelAdmin):
    list_display = ["user", "socket_id"]
    search_fields = ["user"]
