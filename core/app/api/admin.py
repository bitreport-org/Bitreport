from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response
from flask import Flask, redirect
from flask_basicauth import BasicAuth

from .database import db, Level, Chart


class CustomAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('index.html')


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

        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(self.basic_auth.challenge())


class InactiveAdmin(AuthAdmin):
    can_edit = False
    can_delete = False
    can_create = False


def configure_admin(app: Flask, active: bool = False) -> Admin:
    admin = Admin(app, name='Core', template_mode='bootstrap3', index_view=CustomAdmin())
    basic_auth = BasicAuth(app)

    if active:
        admin.add_view(AuthAdmin(basic_auth, Level, db.session))
        admin.add_view(AuthAdmin(basic_auth, Chart, db.session))

    else:
        admin.add_view(InactiveAdmin(basic_auth, Level, db.session))
        admin.add_view(InactiveAdmin(basic_auth, Chart, db.session))

    return admin
