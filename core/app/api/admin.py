from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import HTTPException, Response
from flask import Flask, redirect
from flask_basicauth import BasicAuth

from .database import db, Level, Chart


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class AuthAdmin(ModelView):
    def __init__(self, basic_auth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basic_auth = basic_auth

    def is_accessible(self):
        if not self.basic_auth.authenticate():
            raise AuthException('Login required')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(self.basic_auth.challenge())


class InactiveAdmin(AuthAdmin):
    an_create = False
    can_edit = False
    can_delete = False


def configure_admin(app: Flask, active: bool = False) -> Admin:
    admin = Admin(app, name='Core', template_mode='bootstrap3')
    basic_auth = BasicAuth(app)

    if active:
        admin.add_view(AuthAdmin(basic_auth, Level, db.session))
        admin.add_view(AuthAdmin(basic_auth, Chart, db.session))

    else:
        admin.add_view(InactiveAdmin(basic_auth, Level, db.session))
        admin.add_view(InactiveAdmin(basic_auth, Chart, db.session))

    return admin
