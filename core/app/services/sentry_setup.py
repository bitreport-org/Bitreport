import sentry_sdk, logging
from sentry_sdk.integrations.flask import FlaskIntegration
import config

def sentry_up(env):
    # Enable Sentry in production
    if env == 'production':
        logging.info('Sentry is up and running')
        sentry_sdk.init(
            dsn=config.BaseConfig.SENTRY_URL,
            integrations=[FlaskIntegration()]
        )
