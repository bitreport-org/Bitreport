import numpy as np

from app.ta.charting import (
    constructors as cts,
    triangles as ts)

from app.ta.charting.base import Setup, Universe
from app.ta.charting import Charting
from app.api.database import Chart
from app.utils.sample_prices import asc_triangle, desc_triangle, symm_triangle


class TrianglesSamples:
    tf = 'test_tf'
    desc_triangle = desc_triangle().close
    asc_triangle = asc_triangle().close
    sym_triangle = symm_triangle().close
    time = np.arange(desc_triangle.size)


class TestTriangles(TrianglesSamples):
    def test_descending(self, app):
        close = self.desc_triangle
        pair = 'test_descending1'
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        with app.ctx:
            triangle = ts.DescTriangle(universe=uni,
                                       bottoms=bottoms,
                                       skews=skews
                                       )
            triangle.save()

        assert isinstance(triangle.setup, Setup)
        assert isinstance(triangle.json(), dict)

        # Assert proper values
        params = triangle.setup.params
        assert isinstance(params, dict)
        assert params['hline'] == 0.0
        assert params['slope'] < 0.0
        assert 'coef' in params.keys()

        # Assert setup is saved
        with app.ctx:
            results = Chart.query.filter_by(
                type=triangle.__name__,
                pair=pair
            ).all()

        assert len(results) == 1
        assert results[0].timeframe == self.tf
        assert results[0].params == params

    def test_desc_no_setup(self):
        pair = 'test_descending2'
        close = self.asc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        triangle = ts.DescTriangle(universe=uni,
                                   bottoms=bottoms,
                                   skews=skews
                                   )

        assert triangle.setup is None

    def test_ascending(self, app):
        pair = 'test_ascending'
        close = self.asc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(bottoms)

        with app.ctx:
            triangle = ts.AscTriangle(universe=uni,
                                      tops=tops,
                                      skews=skews
                                      )
            triangle.save()

        assert isinstance(triangle.setup, Setup)
        assert isinstance(triangle.json(), dict)

        # Assert proper values
        params = triangle.setup.params
        assert isinstance(params, dict)
        assert params['hline'] == 100.0
        assert params['slope'] > 0.0
        assert 'coef' in params.keys()

        # Assert setup is saved
        with app.ctx:
            results = Chart.query.filter_by(
                type=triangle.__name__,
                pair=pair
            ).all()

        assert len(results) == 1
        assert results[0].timeframe == self.tf
        assert results[0].params == params

    def test_asc_no_setup(self):
        pair = 'test_ascending1'
        close = self.desc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        triangle = ts.AscTriangle(universe=uni,
                                  tops=tops,
                                  skews=skews
                                  )

        assert triangle.setup is None

    def test_symmetrical(self, app):
        pair = 'test_symm1'
        close = self.sym_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        downs = cts.skews(bottoms)
        ups = cts.skews(tops)

        with app.ctx:
            triangle = ts.SymmetricalTriangle(universe=uni,
                                              ups=ups,
                                              downs=downs
                                              )
            triangle.save()

        assert isinstance(triangle.setup, Setup)
        assert isinstance(triangle.json(), dict)

        # Assert proper values
        params = triangle.setup.params
        assert isinstance(params, dict)
        (up_slope, _), (down_slope, _) = params.values()
        assert up_slope <= 0.0
        assert down_slope >= 0.0

        # Assert setup is saved
        with app.ctx:
            results = Chart.query.filter_by(
                type=triangle.__name__,
                pair=pair
            ).all()

        assert len(results) == 1
        assert results[0].timeframe == self.tf
        assert results[0].params == {k: list(v) for k, v in params.items()}


class TestCharting(TrianglesSamples):
    def test_asc(self, app):
        pair = 'test_ascending3'
        close = self.asc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time,
            future_time=np.array([])
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(bottoms)

        with app.ctx:
            triangle1 = ts.AscTriangle(universe=uni,
                                       tops=tops,
                                       skews=skews
                                       )
            triangle2 = Charting(universe=uni)()

        assert triangle1.setup
        assert isinstance(triangle2, dict)

        assert isinstance(triangle2['upper_band'], list)
        assert isinstance(triangle2['lower_band'], list)

        json = triangle1.json()
        assert triangle2['info'] == json['info']
        assert triangle2['upper_band'] == json['upper_band']
        assert triangle2['lower_band'] == json['lower_band']
