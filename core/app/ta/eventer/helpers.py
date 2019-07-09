from app.models import Event, db


def add_event(params: dict) -> Event:
    lvl = Event.query.filter_by(**params).first()
    if not lvl:
        lvl = Event(**params)
        db.session.add(lvl)
        db.session.commit()
    return lvl
