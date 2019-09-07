from flask_migrate import Migrate

from config import resolve_config
from app.api.app_factory import create_app
from app.models import db
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

# Celery
celery = make_celery(app)
app.app_context().push()
