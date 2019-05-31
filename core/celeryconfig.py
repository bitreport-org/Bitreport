from celery.schedules import crontab


CELERY_IMPORTS = ('app.queue.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


CELERYBEAT_SCHEDULE = {
    'update-influx': {
        'task': 'app.queue.tasks.fill_influx',
        'schedule': crontab(minute=0, hour='*/1'),
    }
}
