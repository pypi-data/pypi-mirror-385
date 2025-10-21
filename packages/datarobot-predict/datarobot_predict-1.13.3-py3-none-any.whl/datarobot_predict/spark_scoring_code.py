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
# pylint: disable=protected-access
import datetime
import os
from typing import Any, Optional, Sequence, Union

import pandas as pd
from py4j.java_gateway import (  # type: ignore
    JavaClass,
    JavaGateway,
    JavaObject,
    JVMView,
    get_java_class,
)
from pyspark.sql import DataFrame, SparkSession

from datarobot_predict import TimeSeriesType
from datarobot_predict._base_scoring_code import BaseScoringCodeModel

SPARK_API_JAR = os.path.join(os.path.dirname(__file__), "lib", "scoring-code-spark-api.jar")
SPARK_API_JAR = os.environ.get("SPARK_API_JAR", SPARK_API_JAR)


class SparkScoringCodeModel(BaseScoringCodeModel):
    def __init__(self, jar_path: Optional[str] = None, allow_models_in_classpath: bool = False):
        """
        Create a new instance of SparkScoringCodeModel

        Parameters
        ----------
        jar_path: Optional[str]
            The path to a Scoring Code jar file to load.
            If None, the Scoring Code jar will be loaded from the classpath

        allow_models_in_classpath: bool
            Having models in the classpath while loading a model from the filesystem using the
            jar_path argument can lead to unexpected behavior so this is not allowed by default but
            can be forced using allow_models_in_classpath.
            If True, models already present in the classpath will be ignored.
            If False, a ValueError will be raised if models are detected in the classpath.
        """

        if jar_path and not os.path.exists(jar_path):
            raise ValueError(f"File not found: {jar_path}")

        session = SparkSession._instantiatedSession
        if not session:
            raise ValueError("Failed to get active spark session")
        self._spark = session

        jvm = self._spark._jvm
        if not jvm:
            raise Exception("Can't access jvm")
        self._jvm = jvm

        self._sc = self._spark._sc

        self._py4j_helper = _Py4JHelper(self._sc._gateway, self._jvm)

        if jar_path and not allow_models_in_classpath:
            predictors_class = self._jvm.com.datarobot.prediction.Predictors
            if (
                isinstance(predictors_class, JavaClass)
                and predictors_class.getAllPredictors().hasNext()
            ):
                raise ValueError(
                    "Trying to load model from jar file but there are already models present "
                    "in classpath. This can cause issues. Remove models from classpath or "
                    "instantiate model with allow_models_in_classpath=True"
                )

        self._sc._jsc.addJar(SPARK_API_JAR)
        self._disable_url_connection_cache()

        self._class_loader = self._py4j_helper.create_url_class_loader(
            [SPARK_API_JAR],
            parent=self._jvm.java.lang.Thread.currentThread().getContextClassLoader(),
        )

        predictors_class = self._class_loader.loadClass(
            "hidden.com.datarobot.prediction.sparkapi.Predictors"
        )

        if jar_path:
            self._model = self._create_spark_model_from_filesystem(jar_path, predictors_class)
        else:
            self._model = self._create_spark_model_from_classpath(predictors_class)

        predictor = self._py4j_helper.invoke_method(
            "getModel",
            self._model,
        )
        self.__predictor = _PredictorCaller(predictor, self._py4j_helper, self._class_loader)

    def predict(
        self,
        data_frame: Union[DataFrame, pd.DataFrame],
        max_explanations: int = 0,
        threshold_low: Optional[float] = None,
        threshold_high: Optional[float] = None,
        time_series_type: TimeSeriesType = TimeSeriesType.FORECAST,
        forecast_point: Optional[datetime.datetime] = None,
        predictions_start_date: Optional[datetime.datetime] = None,
        predictions_end_date: Optional[datetime.datetime] = None,
    ) -> DataFrame:
        """
        Get predictions from the Scoring Code Spark model.

        Parameters
        ----------
        data_frame: Union[pyspark.sql.DataFrame, pandas.DataFrame]
            Input data.
        time_series_type: TimeSeriesType
            Type of time series predictions to compute.
            If TimeSeriesType.FORECAST, predictions will be computed for a single
            forecast point specified by forecast_point.
            If TimeSeriesType.HISTORICAL, predictions will be computed for the range of
            timestamps specified by predictions_start_date and predictions_end_date.
        forecast_point: Optional[datetime.datetime]
            Forecast point to use for time series forecast point predictions.
            If None, the forecast point is detected automatically.
            If not None and time_series_type is not TimeSeriesType.FORECAST,
            ValueError is raised
        predictions_start_date: Optional[datetime.datetime]
            Start date in range for historical predictions. Inclusive.
            If None, predictions will start from the earliest date in the input that
            has enough history.
            If not None and time_series_type is not TimeSeriesType.HISTORICAL,
            ValueError is raised
        predictions_end_date: Optional[datetime.datetime]
            End date in range for historical predictions. Exclusive.
            If None, predictions will end on the last date in the input.
            If not None and time_series_type is not TimeSeriesType.HISTORICAL,
            ValueError is raised
        max_explanations: int
            Number of prediction explanations to compute.
            If 0, prediction explanations are disabled.
        threshold_high: Optional[float]
            Only compute prediction explanations for predictions above this threshold.
            If None, the default value will be used.
        threshold_low: Optional[float]
            Only compute prediction explanations for predictions below this threshold.
            If None, the default value will be used.


        Returns
        -------
        pyspark.sql.DataFrame
            Prediction output.

        """

        self._validate_predict(
            max_explanations=0,
            threshold_high=None,
            threshold_low=None,
            time_series_type=time_series_type,
            forecast_point=forecast_point,
            predictions_start_date=predictions_start_date,
            predictions_end_date=predictions_end_date,
            prediction_intervals_length=None,
        )

        if isinstance(data_frame, pd.DataFrame):
            data_frame = self._spark.createDataFrame(data_frame)

        time_series_options = self._build_ts_options(
            time_series_type,
            forecast_point,
            predictions_start_date,
            predictions_end_date,
            None,
        )

        self._py4j_helper.invoke_method(
            "options_$eq",
            self._model,
            arguments=[time_series_options],
            argument_types=[
                self._class_loader.loadClass("com.datarobot.prediction.TimeSeriesOptions")
            ],
        )
        explanation_params = self._build_explanation_params(
            max_explanations=max_explanations,
            threshold_high=threshold_high,
            threshold_low=threshold_low,
        )

        self._py4j_helper.invoke_method(
            "explanationParams_$eq",
            self._model,
            arguments=[explanation_params],
            argument_types=[
                self._class_loader.loadClass("com.datarobot.prediction.ExplanationParams")
            ],
        )

        java_dataframe = self._py4j_helper.invoke_method(
            "transform",
            self._model,
            arguments=[data_frame._jdf],
            argument_types=[self._jvm.org.apache.spark.sql.Dataset],
        )

        return DataFrame(java_dataframe, data_frame.sql_ctx)

    @property
    def _predictor(self) -> Any:
        return self.__predictor

    def _new_time_series_options_builder(self) -> Any:
        return _TimeSeriesOptionsBuilder(self._py4j_helper, self._class_loader)

    def _get_default_explanation_params(self) -> Any:
        return self._model.explanationParams()

    def _create_spark_model_from_classpath(self, predictors_class: Any) -> Any:
        return self._py4j_helper.invoke_method(
            "getPredictor",
            jobject=None,
            clazz=predictors_class,
        )

    def _create_spark_model_from_filesystem(self, jar_path: str, predictors_class: Any) -> Any:
        current_thread = self._jvm.java.lang.Thread.currentThread()

        model_id = self._get_model_id_from_jar(jar_path)
        original_loader = current_thread.getContextClassLoader()
        try:
            current_thread.setContextClassLoader(self._class_loader)
            return self._py4j_helper.invoke_method(
                "getPredictor",
                jobject=None,
                clazz=predictors_class,
                arguments=[jar_path, model_id],
                argument_types=[
                    self._jvm.java.lang.String,
                    self._jvm.java.lang.String,
                ],
            )
        finally:
            current_thread.setContextClassLoader(original_loader)

    def _disable_url_connection_cache(self) -> None:
        # Call setDefaultUseCaches which will disable caching for all URLs. This makes it possible
        # to overwrite a jar file with a new version and instantiate the new model. When caching
        # is enabled, the old file will be reused in some cases and weird things happen.
        url = self._jvm.java.io.File(SPARK_API_JAR).toURI().toURL()
        conn = url.openConnection()
        conn.setDefaultUseCaches(False)

    def _get_model_id_from_jar(self, jar_path: str) -> str:
        loader = self._py4j_helper.create_url_class_loader([jar_path])
        predictors_class = loader.loadClass("com.datarobot.prediction.Predictors")
        predictor = self._py4j_helper.invoke_method(
            "getPredictor",
            jobject=None,
            clazz=predictors_class,
            arguments=[loader],
            argument_types=[self._jvm.java.lang.ClassLoader],
        )

        info_class = loader.loadClass("com.datarobot.prediction.IPredictorInfo")
        return str(
            self._py4j_helper.invoke_method("getModelId", jobject=predictor, clazz=info_class)
        )


class _Py4JHelper:
    def __init__(self, gateway: JavaGateway, view: JVMView):
        self._gateway = gateway
        self._view = view

    def create_url_class_loader(self, paths: Sequence[str], parent: Any = "default") -> Any:
        """
        Create url class loader from filesystem paths.

        Parameters
        ----------
        paths: Sequence[str]
            Sequence of filesystem paths.
        parent: Any
            The parent classloader to use.
            If default, URLClassLoader will use the default parent.
        Returns
        -------
        URLClassLoader
        """
        urls = [self._view.java.io.File(path).toURI().toURL() for path in paths]
        url_array = self.new_array(urls, jtype=self._view.java.net.URL)

        if parent == "default":
            return self._view.java.net.URLClassLoader(url_array)

        return self._view.java.net.URLClassLoader(url_array, parent)

    def invoke_method(
        self,
        method_name: str,
        jobject: Optional[JavaObject] = None,
        clazz: Optional[JavaClass] = None,
        arguments: Optional[Sequence[Any]] = None,
        argument_types: Optional[Sequence[Union[JavaClass, JavaObject]]] = None,
    ) -> JavaObject:
        """
        Invoke a Java method using reflection. Useful when classloaders are used together with Py4J

        Parameters
        ----------
        method_name: str
            Name of method.
        jobject: Optional[JavaObject]
            Object that method should be invoked on.
            If None, method is a static method and clazz parameter should be specified.
        clazz: Optional[JavaClass]
            Java class that defines method to be invoked.
            If None, class will be queried from jobject
        arguments: Optional[Sequence[Any]]
            Arguments to method.
        argument_types: Optional[Sequence[Union[JavaClass, JavaObject]]]
            Types of arguments.
        Returns
        -------
        JavaObject
            Return value from method invocation.
        """
        if clazz is None:
            if jobject is None:
                raise ValueError("At least one of jobject,clazz has to be specified")
            clazz = jobject.getClass()
        if arguments is None:
            arguments = []
        if argument_types is None:
            argument_types = []

        types = [get_java_class(t) if isinstance(t, JavaClass) else t for t in argument_types]
        method = clazz.getMethod(
            method_name,
            self.new_array(types, jtype=self._view.java.lang.Class),
        )
        return method.invoke(jobject, self.new_array(arguments))

    def new_array(self, contents: Sequence[Any], jtype: Optional[JavaClass] = None) -> JavaObject:
        """
        Create new Java array from sequence.

        Parameters
        ----------
        contents: Sequence[Any]
            Contents of new array.
        jtype: Optional[JavaClass]
            Types of contents.
            If None, java.lang.Object is used.
        Returns
        -------
        JavaObject
            Java array.
        """
        if jtype is None:
            jtype = self._view.java.lang.Object

        arr = self._gateway.new_array(jtype, len(contents))
        for i, el in enumerate(contents):
            if el is not None:
                arr[i] = el

        return arr


class _PredictorCaller:
    def __init__(self, predictor: JavaObject, py4j_helper: _Py4JHelper, class_loader: JavaObject):
        self._predictor = predictor
        self._py4j_helper = py4j_helper
        self._class_loader = class_loader

    def __getattr__(self, item: str) -> Any:
        FUNCTIONS = {
            "getModelId": "IPredictorInfo",
            "getFeatures": "IPredictorInfo",
            "getPredictorClass": "IPredictorInfo",
            "getModelInfo": "IPredictorInfo",
            "getClassLabels": "IClassificationPredictor",
            "getSeriesIdColumnName": "ITimeSeriesModelInfo",
            "getTimeStep": "ITimeSeriesModelInfo",
            "getDateColumnName": "ITimeSeriesModelInfo",
            "getFeatureDerivationWindow": "ITimeSeriesModelInfo",
            "getForecastWindow": "ITimeSeriesModelInfo",
            "getDateFormat": "ITimeSeriesModelInfo",
            "getDefaultPredictionExplanationParams": "IPredictorInfo",
        }

        clazz = self._class_loader.loadClass(f"com.datarobot.prediction.{FUNCTIONS[item]}")

        def func() -> JavaObject:
            return self._py4j_helper.invoke_method(item, jobject=self._predictor, clazz=clazz)

        return func


class _TimeSeriesOptionsBuilder:
    def __init__(self, py4j_helper: _Py4JHelper, class_loader: JavaObject):
        self._py4j_helper = py4j_helper
        self._class_loader = class_loader

        self._classes = {
            "TimeSeriesOptions": self._class_loader.loadClass(
                "com.datarobot.prediction.TimeSeriesOptions"
            ),
            "String": self._class_loader.loadClass("java.lang.String"),
        }
        self._builder = self._py4j_helper.invoke_method(
            "newBuilder", clazz=self._classes["TimeSeriesOptions"]
        )

    # pylint: disable=missing-function-docstring
    def buildSingleForecastPointRequest(self, forecast_point: Optional[str] = None) -> JavaObject:
        arguments = [forecast_point] if forecast_point else []
        argument_types = [self._classes["String"]] if forecast_point else []
        return self._py4j_helper.invoke_method(
            "buildSingleForecastPointRequest",
            jobject=self._builder,
            arguments=arguments,
            argument_types=argument_types,
        )

    # pylint: disable=missing-function-docstring
    def buildForecastDateRangeRequest(self, start_date: str, end_date: str) -> JavaObject:
        return self._py4j_helper.invoke_method(
            "buildForecastDateRangeRequest",
            jobject=self._builder,
            arguments=[start_date, end_date],
            argument_types=[self._classes["String"], self._classes["String"]],
        )
