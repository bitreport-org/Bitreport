from flask import Flask, redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from app.models import Chart, Event, db


class CustomAdmin(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("index.html")


class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(
            message,
            Response(
                "You could not be authenticated. Please refresh the page.",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            ),
        )


class AuthAdmin(ModelView):
    def __init__(self, basic_auth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basic_auth = basic_auth

    def is_accessible(self):
        if not self.basic_auth.authenticate():
            raise AuthException("Login required")

        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(self.basic_auth.challenge())


class InactiveAdmin(AuthAdmin):
    can_edit = False
    can_delete = True
    can_create = False


def configure_admin(app: Flask, active: bool = False) -> Admin:
    basic_auth = BasicAuth(app)

    if active:
        index_view = CustomAdmin()
        admin_type = AuthAdmin
    else:
        index_view = CustomAdmin(url="/core/admin")
        admin_type = InactiveAdmin

    admin = Admin(app, name="Core", template_mode="bootstrap3", index_view=index_view)
    admin.add_view(admin_type(basic_auth, Chart, db.session))
    admin.add_view(admin_type(basic_auth, Event, db.session))

    return admin
