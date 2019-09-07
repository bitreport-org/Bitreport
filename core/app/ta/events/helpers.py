from app.models import Event, db


def add_peak(params: dict, strength: int) -> Event:
    evt = Event.query.filter_by(**params).first()
    if evt is None:
        params["strength"] = strength
        evt = Event(**params)
        db.session.add(evt)
        db.session.commit()
    elif evt.strength < strength:
        evt.strength = strength
        db.session.commit()
    return evt
