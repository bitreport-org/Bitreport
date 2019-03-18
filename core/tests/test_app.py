class TestApp:
    def test_app_init(self, app):
        rv = app.get('/')
        assert rv.status_code == 200
        assert b'Wrong place, is it' in rv.data

