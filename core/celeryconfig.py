from celery.schedules import crontab


CELERY_IMPORTS = ('app.creator.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'app.creator.tasks.fill_influx',
        'schedule': crontab(minute=0, hour='*/1'),
    }
}
