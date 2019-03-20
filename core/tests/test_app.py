class TestApp:
    def test_app_init(self, app):
        rv = app.get('/')
        assert rv.status_code == 200
        assert b'Wrong place, is it' in rv.data


    def test_no_pair(self, app):
        response = app.post('/fill')
        assert response.status_code == 404, 'Wrong code'