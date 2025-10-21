#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
import enum
import functools
import re
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Optional, Sequence, Tuple, Callable

from py4j.java_gateway import JavaObject  # type: ignore
from py4j.protocol import Py4JJavaError  # type: ignore

from datarobot_predict import TimeSeriesType


class ModelType(enum.Enum):
    CLASSIFICATION = "IClassificationPredictor"
    """Classification predictor"""
    REGRESSION = "IRegressionPredictor"
    """Regression predictor"""
    TIME_SERIES = "ITimeSeriesRegressionPredictor"
    """Time Series predictor"""
    GENERIC = "GenericPredictorImpl"
    """Generic predictor. Used for testing purposes."""


class ScoringCodeJavaError(Exception):
    def __init__(self, java_error: Py4JJavaError):
        self.str = str(java_error)
        self.class_name = java_error.java_exception.getClass().getName()
        self.message = java_error.java_exception.getMessage()

    def __str__(self) -> str:
        return self.str


def _wrap_java_exception(func: Callable[..., Any]) -> Any:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Call the original function
            return func(*args, **kwargs)
        except Py4JJavaError as e:
            raise ScoringCodeJavaError(e).with_traceback(e.__traceback__) from None

    return wrapper


class BaseScoringCodeModel(ABC):
    @property
    @_wrap_java_exception
    def series_id_column(self) -> Optional[str]:
        """
        Get the name of the series id column for a Time Series model.

        Returns
        -------
        Optional[str]
            Name of the series id column if model has one, else None.
        """
        return (
            str(self._predictor.getSeriesIdColumnName())
            if self.model_type == ModelType.TIME_SERIES
            else None
        )

    @property
    @_wrap_java_exception
    def class_labels(self) -> Optional[Sequence[str]]:
        """
        Get the class labels for the model.

        Returns
        -------
        Optional[Sequence[str]]
            List of class labels if model is a classification model, else None.
        """
        return (
            [str(label) for label in self._predictor.getClassLabels()]
            if self.model_type == ModelType.CLASSIFICATION
            else None
        )

    @property
    @_wrap_java_exception
    def features(self) -> Dict[str, type]:
        """
        Get features names and types for the model.

        Returns
        -------
        OrderedDict[str, type]
            Dictionary mapping feature name to feature type, where feature type is
            either str or float. The ordering of features is the same as it was during
            model training.
        """

        def feature_type(java_type: Any) -> type:
            simple = java_type.getSimpleName()
            if simple == "Double":
                return float
            if simple == "String":
                return str
            raise RuntimeError(f"Unexpected java type {simple}")

        features = OrderedDict()
        for key, val in self._predictor.getFeatures().items():
            features[key] = feature_type(val)
        return features

    @property
    @_wrap_java_exception
    def time_step(self) -> Optional[Tuple[int, str]]:
        """
        Get the time step for a Time Series model.

        Returns
        -------
        Optional[Tuple[int, str]]
            Time step as (quantity, time unit) if model has this, else None.
            Example: (3, "DAYS")
        """
        if self.model_type != ModelType.TIME_SERIES:
            return None

        step = self._predictor.getTimeStep()
        return int(step.getKey()), str(step.getValue())

    @property
    @_wrap_java_exception
    def date_column(self) -> Optional[str]:
        """
        Get the date column for a Time Series model.

        Returns
        -------
        Optional[str]
            Name of date column if model has one, else None.
        """
        return (
            str(self._predictor.getDateColumnName())
            if self.model_type == ModelType.TIME_SERIES
            else None
        )

    @property
    @_wrap_java_exception
    def model_info(self) -> Optional[Dict[str, str]]:
        """
        Get model metadata.

        Returns
        -------
        Optional[Dict[str, str]]
            Dictionary with metadata if model has any, else None
        """
        info = self._predictor.getModelInfo()
        if not info:
            return None
        return {str(key): str(val) for key, val in info.items()}

    @property
    @_wrap_java_exception
    def feature_derivation_window(self) -> Optional[Tuple[int, int]]:
        """
        Get the feature derivation window for a Time Series model.

        Returns
        -------
        Optional[Tuple[int, int]]
            Feature derivation window as (begin, end) if model has this, else None.
        """
        if self.model_type != ModelType.TIME_SERIES:
            return None

        window = self._predictor.getFeatureDerivationWindow()
        return int(window.getKey()), int(window.getValue())

    @property
    @_wrap_java_exception
    def model_type(self) -> ModelType:
        """
        Get the model type.

        Returns
        -------
        ModelType
            One of: ModelType.CLASSIFICATION, ModelType.REGRESSION, ModelType.TIME_SERIES
        """
        clazz = self._predictor.getPredictorClass().getSimpleName()
        return ModelType(clazz)

    @property
    @_wrap_java_exception
    def forecast_window(self) -> Optional[Tuple[int, int]]:
        """
        Get the forecast window for a Time Series model.

        Returns
        -------
        Optional[Tuple[int, int]]
            Forecast window as (begin, end) if model has this, else None.
        """
        if self.model_type != ModelType.TIME_SERIES:
            return None

        window = self._predictor.getForecastWindow()
        return int(window.getKey()), int(window.getValue())

    @property
    @_wrap_java_exception
    def date_format(self) -> Optional[str]:
        """
        Get the date format for a Time Series model.

        Returns
        -------
        Optional[str]
            Date format having the syntax expected by datetime.strftime() or None
            if model is not time series.
        """
        if self.model_type != ModelType.TIME_SERIES:
            return None
        return _java_date_format_to_python(str(self._predictor.getDateFormat()))

    @property
    @_wrap_java_exception
    def model_id(self) -> str:
        """
        Get the model id.

        Returns
        -------
        str
            The model id.
        """
        return str(self._predictor.getModelId())

    @property
    @abstractmethod
    def _predictor(self) -> Any:
        pass

    @abstractmethod
    def _new_time_series_options_builder(self) -> Any:
        pass

    @abstractmethod
    def _get_default_explanation_params(self) -> Any:
        pass

    def _validate_predict(
        self,
        max_explanations: int = 0,
        threshold_high: Optional[float] = None,
        threshold_low: Optional[float] = None,
        time_series_type: TimeSeriesType = TimeSeriesType.FORECAST,
        forecast_point: Optional[datetime.datetime] = None,
        predictions_start_date: Optional[datetime.datetime] = None,
        predictions_end_date: Optional[datetime.datetime] = None,
        prediction_intervals_length: Optional[int] = None,
    ) -> None:
        if prediction_intervals_length is not None and (
            prediction_intervals_length < 1 or prediction_intervals_length > 100
        ):
            raise ValueError("Prediction intervals length must be >0 and <=100")

        if threshold_high and not max_explanations:
            raise ValueError(
                "threshold_high does not make sense without specifying max_explanations"
            )
        if threshold_low and not max_explanations:
            raise ValueError(
                "threshold_low does not make sense without specifying max_explanations"
            )

        if self.model_type == ModelType.TIME_SERIES:
            if time_series_type == TimeSeriesType.FORECAST:
                if predictions_start_date:
                    raise ValueError(
                        "Predictions start date is not supported when time_series_type is FORECAST"
                    )
                if predictions_end_date:
                    raise ValueError(
                        "Predictions end date is not supported when time_series_type is FORECAST"
                    )
            else:
                if forecast_point:
                    raise ValueError(
                        "Forecast point is not supported when time_series_type is HISTORICAL"
                    )
        else:
            if forecast_point:
                raise ValueError("forecast_point is not supported by non time series models")

            if time_series_type != TimeSeriesType.FORECAST:
                raise ValueError("time_series_type is not supported by non time series models")

            if predictions_start_date:
                raise ValueError(
                    "predictions_start_date is not supported by non time series models"
                )

            if predictions_end_date:
                raise ValueError("predictions_end_date is not supported by non time series models")

    def _build_ts_options(
        self,
        time_series_type: TimeSeriesType,
        forecast_point: Optional[datetime.datetime],
        predictions_start_date: Optional[datetime.datetime],
        predictions_end_date: Optional[datetime.datetime],
        prediction_intervals_length: Optional[int],
    ) -> Optional[JavaObject]:
        if self.model_type != ModelType.TIME_SERIES:
            return None

        builder = self._new_time_series_options_builder()
        if prediction_intervals_length:
            builder.computeIntervals(True)
            builder.setPredictionIntervalLength(prediction_intervals_length)

        assert self.date_format is not None
        if time_series_type == TimeSeriesType.FORECAST:
            if forecast_point:
                options = builder.buildSingleForecastPointRequest(
                    forecast_point.strftime(self.date_format)
                )
            else:
                options = builder.buildSingleForecastPointRequest()
        else:
            start_date = (
                predictions_start_date.strftime(self.date_format)
                if predictions_start_date
                else None
            )
            end_date = (
                predictions_end_date.strftime(self.date_format) if predictions_end_date else None
            )
            options = builder.buildForecastDateRangeRequest(start_date, end_date)

        return options

    def _build_explanation_params(
        self,
        max_explanations: int = 0,
        threshold_high: Optional[float] = None,
        threshold_low: Optional[float] = None,
    ) -> Optional[JavaObject]:
        if max_explanations == 0:
            return None
        params = self._get_default_explanation_params()
        params = params.withMaxCodes(int(max_explanations))
        if threshold_low:
            params = params.withThresholdLow(float(threshold_low))
        if threshold_high:
            params = params.withThresholdHigh(float(threshold_high))
        return params


def _java_date_format_to_python(java_format: str) -> str:
    # The order is important. Longer identifiers needs to come before shorter ones
    # yyyy before yy and MM before M
    replace = OrderedDict(
        [
            ("%", "%%"),
            ("yyyy", "%Y"),
            ("yy", "%y"),
            ("a", "%p"),
            ("E", "%a"),
            ("dd", "%d"),
            ("MM", "%m"),
            ("M", "%b"),
            ("HH", "%H"),
            ("hh", "%I"),
            ("mm", "%M"),
            ("S", "%f"),
            ("ss", "%S"),
            ("Z", "%z"),
            ("z", "%Z"),
            ("D", "%j"),
            ("w", "%U"),
            ("'T'", "T"),
            ("'Z'", "Z"),
        ]
    )

    return re.sub("|".join(replace.keys()), lambda match: replace[match[0]], java_format)
