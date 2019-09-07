from celery import Celery

import celeryconfig


def make_celery(app):
    # create context tasks in celery
    celery = Celery(app.import_name, broker=app.config["BROKER"])
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
