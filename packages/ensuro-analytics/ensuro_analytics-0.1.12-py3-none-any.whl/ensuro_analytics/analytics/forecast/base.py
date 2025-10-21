from dataclasses import dataclass

import numpy as np


@dataclass
class ForecastResult:
    forecasts: np.ndarray

    @property
    def results(self):
        return self.forecasts

    @property
    def average(self):
        return np.nanmean(self.forecasts)

    @property
    def avg(self):
        return self.average

    def distribution(self, bins: int | list[float] | None = 50):
        return np.histogram(self.forecasts, bins=bins)

    def median(self):
        return np.nanmedian(self.forecasts)

    def percentile(self, q: float | list[float]):
        return np.nanpercentile(self.forecasts, q)

    def p(self, q: float | list[float]):
        return self.percentile(q)

    def quantile(self, q: float | list[float]):
        return self.percentile(q)

    def q(self, q: float | list[float]):
        return self.quantile(q)
