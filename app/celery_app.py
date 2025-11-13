from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import os

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'app',
    broker=redis_url,
    backend=redis_url
)

app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'check-courses-every-2-minutes': {
        'task': 'app.tasks.check_courses',
        # 'schedule': crontab(minute='*/2'),
        'schedule': timedelta(seconds=10),
    },
}

app.autodiscover_tasks(['app'])