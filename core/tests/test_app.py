import pytest

class TestApp:
    def test_app_init(self, app):
        rv = app.get('/')
        assert rv.status_code == 200
        assert b'Wrong place, is it' in rv.data


    def test_no_pair(self, app):
        response = app.post('/fill')
        assert response.status_code == 404, 'Wrong code'

    def test_404(self, app):
        response = app.get('/lsjdfs/erwre')
        assert response.status_code == 404
        assert isinstance(response.get_json(), dict)

        r = response.get_json()
        assert 'msg' in r.keys()
        assert r['msg'] == 'Wrong place!'

    def test_500(self, app):
        with pytest.raises(ZeroDivisionError):
            response = app.get('/test/bad/error')

            assert response.status_code == 500
            assert isinstance(response.get_json(), dict)

            r = response.get_json()
            assert 'msg' in r.keys()
            assert r['msg'] == 'Server is dead :( '
