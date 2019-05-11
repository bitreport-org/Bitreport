import numpy as np

from app.ta.charting import (
    constructors as cts,
    triangles as ts)

from app.ta.charting.triangle import Setup, Universe
from app.ta.charting import Charting
from app.api.database import Chart
from app.utils.sample_prices import asc_triangle, desc_triangle


class TrianglesSamples:
    tf = 'test_tf'
    desc_triangle = desc_triangle().close
    asc_triangle = asc_triangle().close
    time = np.arange(desc_triangle.size)


class TestTriangles(TrianglesSamples):
    def test_descending(self, app):
        close = self.desc_triangle
        pair = 'test_descending'
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        with app.ctx:
            triangle = ts.DescTriangle(universe=uni,
                                       bottoms=bottoms,
                                       skews=skews
                                       )

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
        pair = 'test_descending'
        close = self.asc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time
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
            time=self.time
        )

        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(bottoms)

        with app.ctx:
            triangle = ts.AscTriangle(universe=uni,
                                      tops=tops,
                                      skews=skews
                                      )

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
        pair = 'test_ascending'
        close = self.desc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time
        )

        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        triangle = ts.AscTriangle(universe=uni,
                                  tops=tops,
                                  skews=skews
                                  )

        assert triangle.setup is None


class TestCharting(TrianglesSamples):
    def test_asc(self, app):
        pair = 'test_ascending'
        close = self.asc_triangle
        uni = Universe(
            pair=pair,
            timeframe=self.tf,
            close=close,
            time=self.time
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
