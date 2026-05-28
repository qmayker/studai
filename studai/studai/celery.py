import os 
from time import sleep
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studai.settings')

app = Celery('studai')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task()
def generate_questions(chat_related_id:int):
    from chat.models import Chat
    Chat.objects.get(related_id=chat_related_id)
    sleep(5) 
    