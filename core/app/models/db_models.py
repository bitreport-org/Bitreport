from app.models.utils import db


class Level(db.Model):
    """
    Creates Level.

    Parameters
    ----------
    pair: pair name ex. 'BTCUSD'
    timeframe: timeframe ex. '1h'
    type: name of level type
    value: value of the level
    """
    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())

    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    first_occurrence = db.Column(db.Integer)
    type = db.Column(db.String)
    strength = db.Column(db.Integer)
    value = db.Column(db.Float, index=True)


class Chart(db.Model):
    """
    Creates Chart.

    Parameters
    ----------
    pair: pair name ex. 'BTCUSD'
    timeframe: timeframe ex. '1h'
    type: name of charting setup
    params: params of the setup
    """
    __tablename__ = 'charting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())
    type = db.Column(db.String)
    params = db.Column(db.JSON)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    time = db.Column(db.Integer)
    value = db.Column(db.Float)
    name = db.Column(db.String)
    strength = db.Column(db.Integer, default=None)
