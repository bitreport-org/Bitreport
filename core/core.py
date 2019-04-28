import os
from app.api import create_app, db
from app.api.database import Chart, Level, connect_influx
from flask_migrate import Migrate
from config import Development, Production

# Setup proper config
environment = {'development': Development, 'production': Production}
Config = environment[os.environ['FLASK_ENV']]

# Create influx connection
influx = connect_influx(Config.INFLUX)

# Create app
app = create_app(Config, influx)

# Migrations
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Chart=Chart, Level=Level)
