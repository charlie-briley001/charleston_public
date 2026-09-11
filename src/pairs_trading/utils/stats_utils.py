"""Statistical utility functions for time-series analysis.

Provides ADF stationarity testing, cointegration testing, and spread
computation, primarily intended for use in pairs-trading workflows.
"""

from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.tsa.stattools import adfuller, coint

from src.pairs_trading.exceptions.exceptions_stats_utils import StatsUtilsDataTypeError


@dataclass
class AdfData:
    """Container for Augmented Dickey-Fuller test results.

    Attributes:
        test_stat: ADF test statistic.
        p_value: p-value for the test statistic.
        lags: Number of lags used in the regression.
        observations: Number of observations used after adjusting for lags.
    """

    test_stat: float
    p_value: float
    lags: int
    observations: int


class StatsUtils:
    """Static utility class for time-series statistical tests.

    All methods are stateless and exposed as static methods. The class
    wrapper is kept to allow future shared state or cross-method interaction
    if needed.
    """

    @staticmethod
    def adf_test(
        data_series: Union[pd.Series, npt.NDArray],
        regression_method: str = "ct",
    ) -> AdfData:
        """Run an Augmented Dickey-Fuller test on a time series.

        NaN values are dropped before the test is applied. If a NumPy array
        is passed it is converted to a ``pd.Series`` internally.

        Args:
            data_series (Union[pd.Series, npt.NDArray]): The time series to
                test for a unit root.
            regression_method (str): Regression passed to
                ``statsmodels.tsa.stattools.adfuller``. 

        Returns:
            AdfData: Dataclass containing the test statistic, p-value, lag
            count, and observation count.

        Raises:
            StatsUtilsDataTypeError: If ``data_series`` is not a ``pd.Series`` or
                ``np.ndarray``.
        """
        if not isinstance(data_series, (pd.Series, np.ndarray)):
            raise StatsUtilsDataTypeError(
                "data_series must be a pd.Series or np.ndarray, "
                f"got {type(data_series).__name__}."
            )
        if isinstance(data_series, np.ndarray):
            data_series = pd.Series(data_series)

        output = adfuller(data_series.dropna(), regression=regression_method)
        return AdfData(
            test_stat=output[0],
            p_value=output[1],
            lags=int(output[2]),
            observations=int(output[3]),
        )

    @staticmethod
    def stationarity_test(
        adf_result: Optional[Union[AdfData, dict]] = None,
        test_p_val: Optional[float] = 0.05,
        data_series: Optional[Union[npt.NDArray, pd.Series]] = None,
    ) -> bool:
        """Determine whether a time series is stationary via the ADF test.

        Either a pre-computed ``adf_result`` or a raw ``data_series`` must be
        supplied. If both are provided, ``adf_result`` takes priority and
        ``data_series`` is ignored.

        Args:
            adf_result (Optional[Union[AdfData, dict]]): Pre-computed ADF
                results as an ``AdfData`` instance or an equivalent dict. If
                ``None``, ``data_series`` is required. Defaults to ``None``.
            test_p_val (Optional[float]): Significance level used to reject
                the null hypothesis of a unit root. Must be in the open
                interval ``(0, 1)``. Defaults to ``0.05``.
            data_series (Optional[Union[npt.NDArray, pd.Series]]): Raw time
                series used to compute the ADF test when ``adf_result`` is
                not provided. Defaults to ``None``.

        Returns:
            bool: ``True`` if the series is stationary (p-value <=
            ``test_p_val``), ``False`` otherwise.

        Raises:
            StatsUtilsDataTypeError: If ``test_p_val`` is not a numeric type or is outside
                ``(0, 1)``.
            StatsUtilsDataTypeError: If both ``adf_result`` and ``data_series`` are
                ``None``.
            StatsUtilsDataTypeError: If ``adf_result`` is not an ``AdfData``, dict, or
                ``None``.
        """
        if not isinstance(test_p_val, (float, int)):
            raise StatsUtilsDataTypeError("test_p_val must be a float.")
        if not (0 < test_p_val < 1):
            raise StatsUtilsDataTypeError("test_p_val must be between 0 and 1.")

        if adf_result is None:
            if data_series is None:
                raise StatsUtilsDataTypeError(
                    "data_series must be provided when adf_result is None."
                )
            adf_result = StatsUtils.adf_test(data_series)
        elif isinstance(adf_result, dict):
            adf_result = AdfData(**adf_result)

        if not isinstance(adf_result, AdfData):
            raise StatsUtilsDataTypeError(
                "adf_result must be an AdfData instance, a dict, or None."
            )

        return adf_result.p_value <= test_p_val

    @staticmethod
    def compute_coint_spread(
        series_1: Union[pd.Series, npt.NDArray],
        series_2: Union[pd.Series, npt.NDArray],
    ) -> pd.Series:
        """Compute the OLS residual spread between two series.

        The two series are inner-joined on their indices and rows containing
        NaN values are dropped before fitting, ensuring length consistency.
        ``series_2`` is used as the independent variable (regressor) and
        ``series_1`` as the dependent variable.

        Args:
            series_1 (Union[pd.Series, npt.NDArray]): Dependent time series
                (y in the OLS regression).
            series_2 (Union[pd.Series, npt.NDArray]): Independent time series
                (X in the OLS regression).

        Returns:
            pd.Series: OLS residuals representing the cointegration spread.
        """
        df = pd.concat([series_1, series_2], axis=1).dropna()
        X: pd.DataFrame = sm.add_constant(df.iloc[:, 1])
        model: RegressionResultsWrapper = sm.OLS(df.iloc[:, 0], X).fit()
        spread: pd.Series = model.resid
        return spread

    @staticmethod
    def cointegration_test(
        series_1: Union[pd.Series, npt.NDArray],
        series_2: Union[pd.Series, npt.NDArray],
        p_value: Union[int, float] = 0.05,
    ) -> bool:
        """Test whether two time series are cointegrated.

        Uses the Engle-Granger two-step cointegration test via
        ``statsmodels.tsa.stattools.coint``. The two series are inner-joined
        and NaN rows are dropped before the test is applied.

        Args:
            series_1 (Union[pd.Series, npt.NDArray]): First time series.
            series_2 (Union[pd.Series, npt.NDArray]): Second time series.
            p_value (Union[int, float]): Significance level for the
                cointegration test. Defaults to ``0.05``.

        Returns:
            bool: ``True`` if the series are cointegrated at the given
            significance level, ``False`` otherwise.
        """
        df = pd.concat([series_1, series_2], axis=1).dropna()
        _, test_p_value, _ = coint(df.iloc[:, 0], df.iloc[:, 1])
        return test_p_value <= p_value

