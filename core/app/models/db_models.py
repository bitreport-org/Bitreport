from typing import Optional

from app.models.skew import Skew
from app.models.utils import db


class Chart(db.Model):
    __tablename__ = "charting"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    time = db.Column(db.Integer)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)

    type = db.Column(db.String)

    slope_up = db.Column(db.Float, default=None)
    slope_down = db.Column(db.Float, default=None)
    coef_up = db.Column(db.Float, default=None)
    coef_down = db.Column(db.Float, default=None)

    @property
    def skew(self) -> Optional[Skew]:
        up = self.upper
        down = self.lower
        if up and down:
            return None
        return up or down

    @property
    def upper(self) -> Optional[Skew]:
        if not all([self.slope_up, self.coef_up, self.time]):
            return None
        return Skew(slope=self.slope_up, coef=self.coef_up, start=self.time)

    @property
    def lower(self) -> Optional[Skew]:
        if not all([self.slope_up, self.coef_up, self.time]):
            return None
        return Skew(slope=self.coef_down, coef=self.coef_down, start=self.time)

    def is_not_crossing(self, time: int) -> bool:
        # Case of triangle / wedge / channel
        if self.lower and self.upper:
            up = self.upper.slope * time + self.upper.coef
            down = self.lower.slope * time + self.lower.coef
            return up >= down
        # Else return true because it only a line
        return True

    def width(self, time: int) -> Optional[float]:
        # Case of triangle / wedge / channel
        if self.lower and self.upper:
            up = self.upper.slope * time + self.upper.coef
            down = self.lower.slope * time + self.lower.coef
            return up - down
        # Else return None because it only a line
        return None

    def is_converging(self) -> bool:
        wedge1 = self.width(self.time)
        wedge2 = self.width(self.time + 100)
        if wedge1 and wedge2 and (wedge2 <= wedge1):
            return True
        # Else return true because it only a line
        return False

    def save(self):
        chart = self.query.filter_by(
            type=self.type,
            pair=self.pair,
            timeframe=self.timeframe,
            time=self.time,
            slope_up=self.slope_up,
            slope_down=self.slope_down,
            coef_up=self.coef_up,
            coef_down=self.coef_down,
        ).first()
        if not chart:
            db.session.add(self)
            db.session.commit()
        db.session.close()


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    time = db.Column(db.Integer)
    value = db.Column(db.Float)
    name = db.Column(db.String)
    strength = db.Column(db.Integer, default=None)

    def save(self):
        event = self.query.filter_by(
            pair=self.pair,
            timeframe=self.timeframe,
            time=self.time,
            value=self.value,
            name=self.name,
        ).first()
        if event is None:
            db.session.add(self)
            db.session.commit()
        elif event.strength < self.strength:
            event.strength = self.strength
            db.session.commit()
        db.session.close()
