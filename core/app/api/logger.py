from flask import request, g, Flask
import colors
import time
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def sentry_init(app: Flask) -> bool:
    """
    Activates Sentry logging.

    Parameters
    ----------
    app: Flask app

    Returns
    -------
    bool
    """
    if app.config.get('SENTRY'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_URL'],
            integrations=[FlaskIntegration()]
        )
        app.logger.info('Sentry is up and running.')
        return True
    return False


def create_msg(response):
    if request.path == '/favicon.ico':
        return colors.color('/favicon.ico', 'yellow')

    if request.path.startswith('/static'):
        return colors.color('/static', 'yellow')

    now = time.time()
    duration = round(now - g.start, 2)
    args = dict(request.args)

    query = " "
    if args:
        query = "?"
        for k, v in args.items():
            query += f'{k}={v}&'

    query = query[:-1]

    msg = f'{request.method} {request.path}{query} {response.status_code} {duration}s'

    if response.status_code < 300:
        return colors.color(msg, 'green')

    if response.status_code < 400:
        return colors.color(msg, 'purple')

    if response.status_code < 500:
        return colors.color(msg, 'yellow')

    return colors.color(msg, 'red')
