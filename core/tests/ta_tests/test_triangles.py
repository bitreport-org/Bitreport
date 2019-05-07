import numpy as np

from app.ta.charting import (
    constructors as cts,
    triangles as ts)

from app.ta.charting.triangle import Setup
from app.api.database import Chart


class TrianglesSamples:
    a = np.arange(50, 101, 2)
    b = np.arange(0, 100, 2)[::-1]
    c = np.arange(1, 70, 2)
    d = np.arange(0, 69, 2)[::-1]
    e = np.arange(1, 30, 2)

    desc_triangle = np.concatenate([a, b, c, d, e])
    asc_triangle = (-1 * desc_triangle) + np.max(desc_triangle)

    time = np.arange(desc_triangle.size)


class TestTriangles(TrianglesSamples):
    tf = 'test_tf'

    def test_descending(self, app):
        pair = 'test_descending'
        close = self.desc_triangle
        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        with app.ctx:
            triangle = ts.DescendingTriangle(pair=pair,
                                             timeframe=self.tf,
                                             close=close,
                                             time=self.time,
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
        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        print(bottoms, tops)
        print(skews)

        triangle = ts.DescendingTriangle(pair=pair,
                                         timeframe=self.tf,
                                         close=close,
                                         time=self.time,
                                         bottoms=bottoms,
                                         skews=skews
                                         )

        assert triangle.setup is None


    def test_ascending(self, app):
        pair = 'test_ascending'
        close = self.asc_triangle
        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(bottoms)

        with app.ctx:
            triangle = ts.AscendingTriangle(pair=pair,
                                             timeframe=self.tf,
                                             close=close,
                                             time=self.time,
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
        bottoms = cts.bottoms(close, self.time)
        tops = cts.tops(close, self.time)
        skews = cts.skews(tops)

        print(bottoms, tops)
        print(skews)

        triangle = ts.AscendingTriangle(pair=pair,
                                         timeframe=self.tf,
                                         close=close,
                                         time=self.time,
                                         tops=tops,
                                         skews=skews
                                         )

        assert triangle.setup is None