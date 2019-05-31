from flask_migrate import Migrate

from config import resolve_config
from app.api import create_app
from app.database import db, Level, Chart
from app.utils.sample_prices import init_samples
from app.queue.worker import make_celery


# Setup proper config
Config = resolve_config()

# Create app
app = create_app(Config)

# Sample data
if Config.DEVELOPMENT or Config.TESTING:
    with app.app_context():
        init_samples()

# Migrations
migrate = Migrate(app, db)

# celery
celery = make_celery(app)
app.app_context().push()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Chart=Chart, Level=Level)
