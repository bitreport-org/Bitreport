from celery import Celery
import celeryconfig

# TODO: setup config


def make_celery(app):
    # create context tasks in celery
    celery = Celery(
        app.import_name,
        broker='redis://redis:6379'
    )
    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                print('Works')
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
