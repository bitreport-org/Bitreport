from flask_sqlalchemy import SQLAlchemy
from app.vendors.flask_influx import InfluxDB

db = SQLAlchemy()

influx_db = InfluxDB()
