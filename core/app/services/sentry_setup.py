import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def sentry_up(env):
    # Enable Sentry in production
    if env == 'production':
        sentry_sdk.init(
            dsn="https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679",
            integrations=[FlaskIntegration()]
        )
