from typing import Optional
from app.models import Chart, ChartTypes, Event, Point, Series, Skew

TOP = "TOP"
BOTTOM = "BOTTOM"


class PrinterMixin:
    verbose = True

    def _print_progress(self, name: str, idx: int, steps: int):
        if self.verbose:
            full = 50
            step = int(idx / steps * full)
            end = "\n" if idx == steps else "\r"
            print(
                f"{name} ",
                "." * step,
                " " * (full - step),
                f"[{int(100 * idx / steps)}%]",
                end=end,
            )


class Atomics(PrinterMixin):
    # size of maximum neighbourhood
    space_size: int = 40

    def __init__(self, series: Series):
        self._pair = series.pair
        self._timeframe = series.timeframe
        self.points = list(series.values(key="close"))

    def detect_top(self, strength: int, peak: Point, neighbours) -> Optional[Event]:
        if not all(peak.y >= p.y for p in neighbours):
            return None

        event = Event(
            pair=self._pair,
            timeframe=self._timeframe,
            time=int(peak.x),
            value=float(peak.y),
            name=TOP,
            strength=strength,
        )
        event.save()
        return event

    def detect_bottom(self, strength: int, peak: Point, neighbours) -> Optional[Event]:
        if not all(peak.y <= p.y for p in neighbours):
            return None
        event = Event(
            pair=self._pair,
            timeframe=self._timeframe,
            time=int(peak.x),
            value=float(peak.y),
            name=BOTTOM,
            strength=strength,
        )
        event.save()
        return event

    @staticmethod
    def neighbourhood(i, xs, n, size: int = 10):
        if (i < size) or (i > n - size):
            return xs[i], None

        return xs[i], xs[i - size : i + size]

    def detect_peak(self, position, close, min_size: int = 10):
        close_size = len(close)
        for strength, size in enumerate(range(min_size, self.space_size)):
            point, ngbr = self.neighbourhood(position, close, close_size, size)
            if ngbr is not None:
                self.detect_top(strength + min_size, point, ngbr)
                self.detect_bottom(strength + min_size, point, ngbr)

    def detect_asymptote(self, line_type):
        """
        Detect support and resistances based on two points.
        """
        name_map = {ChartTypes.SKEW_SUPPORT: BOTTOM, ChartTypes.SKEW_RESISTANCE: TOP}

        peaks = Event.query.filter_by(
            pair=self._pair, timeframe=self._timeframe, name=name_map[line_type]
        ).order_by(Event.time.desc())

        if not peaks:
            return

        peaks = list(peaks)
        zipped = zip(peaks[:-1], peaks[1:])

        for step, (p1, p2) in enumerate(zipped):
            self._print_progress(f"Create {line_type}", step, len(peaks) - 2)
            chart_params = {
                "time": p1.time,
                "type": line_type,
                "timeframe": self._timeframe,
                "pair": self._pair,
            }
            skew = Skew.from_events(p1, p2)
            if line_type == ChartTypes.SKEW_RESISTANCE:
                chart_params["slope_up"] = skew.slope
                chart_params["coef_up"] = skew.coef
            elif line_type == ChartTypes.SKEW_SUPPORT:
                chart_params["slope_down"] = skew.slope
                chart_params["coef_down"] = skew.coef
            else:
                continue
            chart = Chart(**chart_params)
            chart.save()

    @staticmethod
    def _is_trinagle(a: Event, b: Event, c: Event, d: Event) -> bool:
        option1 = (
            a.name == TOP and b.name == BOTTOM and c.name == TOP and d.name == BOTTOM
        )
        option2 = (
            a.name == BOTTOM and b.name == TOP and c.name == BOTTOM and d.name == TOP
        )

        return option1 or option2

    def detect_triangles(self):
        peaks = (
            Event.query.filter_by(pair=self._pair, timeframe=self._timeframe)
            .filter(Event.name.in_([TOP, BOTTOM]))
            .order_by(Event.time.desc())
        )

        if not peaks:
            return

        peaks = list(peaks)
        if len(peaks) < 4:
            return

        zipped = zip(peaks[:-3], peaks[1:-2], peaks[2:-1], peaks[3:])
        for step, (a, b, c, d) in enumerate(zipped):
            self._print_progress(f"Create {ChartTypes.TRIANGLE}", step, len(peaks) - 4)
            if not self._is_trinagle(a, b, c, d):
                continue
            skew1 = Skew.from_events(a, c)
            skew2 = Skew.from_events(b, d)

            chart_params = {
                "time": a.time,
                "type": ChartTypes.TRIANGLE,
                "timeframe": self._timeframe,
                "pair": self._pair,
            }
            if skew1.eval(a.time >= skew2.eval(a.time)):
                chart_params["slope_up"] = skew1.slope
                chart_params["coef_up"] = skew1.coef
                chart_params["slope_down"] = skew2.slope
                chart_params["coef_down"] = skew2.coef
            else:
                chart_params["slope_up"] = skew2.slope
                chart_params["coef_up"] = skew2.coef
                chart_params["slope_down"] = skew1.slope
                chart_params["coef_down"] = skew1.coef
            chart = Chart(**chart_params)
            if chart.is_converging():
                chart.save()

    def find_all_peaks(self, close):
        # close = close[-2 * self.space_size:]
        close_size = len(close)

        for step, neighbourhood_size in enumerate(range(10, self.space_size)):
            self._print_progress("Create events", step, self.space_size - 11)
            for i, _ in enumerate(close[neighbourhood_size:-neighbourhood_size]):
                position = i + neighbourhood_size
                point, ngbr = self.neighbourhood(
                    position, close, close_size, neighbourhood_size
                )
                if not ngbr:
                    continue
                self.detect_top(neighbourhood_size, point, ngbr)
                self.detect_bottom(neighbourhood_size, point, ngbr)

        self.detect_asymptote(ChartTypes.SKEW_SUPPORT)
        self.detect_asymptote(ChartTypes.SKEW_RESISTANCE)
        self.detect_triangles()

    def remake(self, verbose: bool):
        self.verbose = verbose
        self.find_all_peaks(self.points)
