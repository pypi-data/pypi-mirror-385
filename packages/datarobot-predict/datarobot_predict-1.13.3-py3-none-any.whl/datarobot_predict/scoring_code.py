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
# pylint: disable=import-error,import-outside-toplevel
from __future__ import annotations
import datetime
import glob
import os.path
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from io import TextIOWrapper
from typing import Any, List, Optional, Tuple, Union, Set

import click
import pandas as pd
from dateutil.parser import isoparse
from py4j.java_collections import SetConverter  # type: ignore
from py4j.java_gateway import (  # type: ignore
    JavaGateway,
    JavaPackage,
    find_jar_path,
    JavaObject,
)

from datarobot_predict._base_scoring_code import (
    BaseScoringCodeModel,
    ModelType,
    TimeSeriesType,
    _wrap_java_exception,
)


BATCH_PROCESSOR_JAR = os.path.join(os.path.dirname(__file__), "lib", "batch-processor.jar")

BATCH_PROCESSOR_JAR = os.environ.get("BATCH_JAR", BATCH_PROCESSOR_JAR)


class ScoringCodeModel(BaseScoringCodeModel):
    @_wrap_java_exception
    def __init__(
        self,
        jar_path: str,
    ):
        """
        Constructor for ScoringCodeModel

        Parameters
        ----------
        jar_path
            path to a jar file
        """
        if jar_path and not os.path.exists(jar_path):
            raise ValueError(f"File not found: {jar_path}")

        classpath = [BATCH_PROCESSOR_JAR, jar_path]

        enable_java_stderr = os.getenv("ENABLE_JAVA_STDERR", "False").lower() in (
            "true",
            "1",
        )

        self.gateway = self._create_gateway(classpath, enable_java_stderr)

        self.__predictor = self._create_predictor()

        if not enable_java_stderr:
            self.gateway.jvm.java.lang.System.setProperty(
                "hidden.org.slf4j.simpleLogger.defaultLogLevel", "off"
            )

        self.server_socket = self.gateway.jvm.java.net.ServerSocket(
            0, 0, self.gateway.jvm.java.net.InetAddress.getLoopbackAddress()
        )
        self.server_socket.setReuseAddress(True)

        self._executor = ThreadPoolExecutor(max_workers=2)

    @_wrap_java_exception
    def predict(
        self,
        data_frame: pd.DataFrame,
        max_explanations: int = 0,
        threshold_high: Optional[float] = None,
        threshold_low: Optional[float] = None,
        time_series_type: TimeSeriesType = TimeSeriesType.FORECAST,
        forecast_point: Optional[datetime.datetime] = None,
        predictions_start_date: Optional[datetime.datetime] = None,
        predictions_end_date: Optional[datetime.datetime] = None,
        prediction_intervals_length: Optional[int] = None,
        passthrough_columns: Union[str, Set[str], None] = None,
    ) -> pd.DataFrame:
        """
        Get predictions from Scoring Code model.

        Parameters
        ----------
        data_frame: pd.DataFrame
            Input data.
        max_explanations: int
            Number of prediction explanations to compute.
            If 0, prediction explanations are disabled.
        threshold_high: Optional[float]
            Only compute prediction explanations for predictions above this threshold.
            If None, the default value will be used.
        threshold_low: Optional[float]
            Only compute prediction explanations for predictions below this threshold.
            If None, the default value will be used.
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
        prediction_intervals_length: Optional[int]
            The percentile to use for the size for prediction intervals. Has to be an
            integer between 0 and 100(inclusive).
            If None, prediction intervals will not be computed.
        passthrough_columns: Union[str, Set[str], None]
            Columns from the input dataframe to include in with the output.
            If 'all', all input columns will be included.
            If None, no columns will be included.

        Returns
        -------
        pd.DataFrame
            Prediction output.

        """

        self._validate_predict(
            max_explanations,
            threshold_high,
            threshold_low,
            time_series_type,
            forecast_point,
            predictions_start_date,
            predictions_end_date,
            prediction_intervals_length,
        )

        _validate_input(data_frame)

        time_series_options = self._build_ts_options(
            time_series_type,
            forecast_point,
            predictions_start_date,
            predictions_end_date,
            prediction_intervals_length,
        )

        return self._predict(
            data_frame,
            max_explanations,
            threshold_high,
            threshold_low,
            time_series_options,
            passthrough_columns,
        )

    def shutdown(self, shutdown_server: bool = True) -> None:
        if hasattr(self, "gateway"):
            if shutdown_server:
                self.gateway.shutdown()
            else:
                self.gateway.close()
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

    def __enter__(self) -> ScoringCodeModel:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.shutdown()

    def __del__(self) -> None:
        self.shutdown()

    def _create_gateway(self, classpath: List[str], enable_java_stderr: bool) -> JavaGateway:
        jvm_args = os.getenv("JVM_ARGS", "").split()

        return JavaGateway.launch_gateway(
            javaopts=jvm_args,
            classpath=os.pathsep.join(classpath),
            redirect_stderr=(sys.stderr if enable_java_stderr else None),
            jarpath=_find_py4j_jar(),
        )

    def _create_predictor(self) -> JavaObject:
        return self.gateway.jvm.com.datarobot.prediction.Predictors.getPredictor()

    @property
    def _predictor(self) -> Any:
        return self.__predictor

    @property
    def _batch_processor(self) -> JavaPackage:
        return self.gateway.jvm.hidden.com.datarobot.batch.processor

    def _new_time_series_options_builder(self) -> Any:
        return self.gateway.jvm.com.datarobot.prediction.TimeSeriesOptions.newBuilder()

    @_wrap_java_exception
    def _get_default_explanation_params(self) -> Any:
        return self._predictor.getDefaultPredictionExplanationParams()

    def _predict(
        self,
        data_frame: pd.DataFrame,
        max_explanations: int,
        threshold_high: Optional[float],
        threshold_low: Optional[float],
        time_series_options: JavaObject,
        passthrough_columns: Union[str, Set[str], None],
    ) -> pd.DataFrame:
        explanation_params = self._build_explanation_params(
            max_explanations=max_explanations,
            threshold_high=threshold_high,
            threshold_low=threshold_low,
        )

        batch_executor = self._build_batch_executor(
            explanation_params, time_series_options, passthrough_columns
        )

        result = self._run_batch_executor(batch_executor, data_frame)

        if time_series_options:
            result["Timestamp"] = pd.to_datetime(result["Timestamp"])
            result["Forecast Point"] = pd.to_datetime(result["Forecast Point"])
            result["Series Id"] = result["Series Id"].fillna("")

        return result

    def _run_batch_executor(
        self, batch_executor: JavaObject, data_frame: pd.DataFrame
    ) -> pd.DataFrame:
        ReaderFactory = self._batch_processor.io.ReaderFactory
        CallbackFactory = self._batch_processor.engine.callback.CallbackFactory

        try:
            address = (
                self.server_socket.getInetAddress().getHostAddress(),
                self.server_socket.getLocalPort(),
            )

            writer_future = self._executor.submit(_write_dataframe, data_frame, address)
            writer_java_socket = self.server_socket.accept()
            input_reader = self.gateway.jvm.java.io.InputStreamReader(
                writer_java_socket.getInputStream(),
                self.gateway.jvm.java.nio.charset.StandardCharsets.UTF_8,
            )

            # Reader is spawned after writer connection has been accepted. This
            # ensures that reader/writer connections are not mixed up.
            reader_future = self._executor.submit(_read_dataframe, address)
            reader_java_socket = self.server_socket.accept()
            reader = ReaderFactory().getCsvReader(input_reader, ",", '"')
            callback = CallbackFactory().getStreamCallback(
                reader_java_socket.getOutputStream(),
                ",",
                self.gateway.jvm.java.nio.charset.StandardCharsets.UTF_8,
            )

            batch_executor.execute(reader, callback)

            # Close reader socket to make Java workers shutdown
            reader_java_socket.close()

            writer_future.result(timeout=1)

            res = reader_future.result(timeout=3)
            return res

        finally:
            writer_java_socket.close()
            reader_java_socket.close()

    def _build_batch_executor(
        self,
        explanation_params: JavaObject,
        ts_options: JavaObject,
        passthrough_columns: Union[str, Set[str], None],
    ) -> JavaObject:
        BatchExecutorBuilder = self._batch_processor.engine.BatchExecutorBuilder

        builder = BatchExecutorBuilder(self._predictor)
        builder.timeSeriesBatchProcessing(self.model_type == ModelType.TIME_SERIES)
        builder.tsOptions(ts_options)

        if passthrough_columns == "all":
            passthrough_columns = {"All"}

        if passthrough_columns is not None:
            builder.passthroughColumns(
                SetConverter().convert(passthrough_columns, self.gateway._gateway_client)
            )
        if explanation_params:
            builder.explanationsParams(explanation_params)
        return builder.build()


def _find_py4j_jar() -> str:
    path: Optional[str] = find_jar_path()

    if path:
        return path

    # This is a workaround to find py4j jar on Databricks. Databricks adds their own
    # version which is already imported when the notebook is started. Their version
    # of py4j is inside a zipfile at '/databricks/spark/python/lib/py4j-0.10.9.5-src.zip'
    # Py4j fails to load its own jar since it is in the zipfile.
    # Here we try to find the jar that is provided by the py4j version that is installed
    # by pip as a dependency to datarobot-predict. We cross our fingers and hope that
    # it is compatible with the imported py4j version.
    path = next(glob.iglob(os.path.join(sys.prefix, "share/py4j/py4j*.jar")), None)
    if path:
        return os.path.realpath(path)

    # Databricks can also install py4j in another location. e.g.
    # /databricks/python3/lib/python3.8/site-packages/py4j and the jar is located at
    # /databricks/python3/share/py4j/py4j0.10.9.7.jar
    # This code takes care of finding it at that location.
    for p in sys.path:
        path = next(glob.iglob(os.path.join(p, "../../../share/py4j/py4j*.jar")), None)
        if path:
            return os.path.realpath(path)

    return ""


def _write_dataframe(data_frame: pd.DataFrame, address: Tuple[str, int]) -> None:
    with socket.socket() as s:
        s.connect(address)
        with s.makefile("w", newline="\n", encoding="utf-8") as f:
            # 17 significant digits to make sure that floats will not lose precision when
            # deserialized on java side
            data_frame.to_csv(f, index=False, float_format="%.17g", quotechar='"')


def _read_dataframe(address: Tuple[str, int]) -> pd.DataFrame:
    with socket.socket() as s:
        s.connect(address)
        with s.makefile("r", encoding="utf-8") as f:
            df = pd.read_csv(f, float_precision="round_trip")
            return df


def _validate_input(data_frame: pd.DataFrame) -> None:
    for column in data_frame.columns:
        if pd.api.types.is_datetime64_any_dtype(data_frame[column]):  # type: ignore
            raise ValueError(
                f"Column {column} has unsupported type {data_frame[column].dtype}. "
                f"Date/time columns must be converted to string. "
                f"The expected date/time format can be queried "
                f"using ScoringCodeModel.date_format"
            )


@click.command()
@click.argument("model", type=click.Path(exists=True))
@click.argument("input_csv", type=click.File(mode="r"))
@click.argument("output_csv", type=click.File(mode="w"))
@click.option("--forecast_point")
@click.option("--predictions_start_date")
@click.option("--predictions_end_date")
@click.option("--with_explanations", is_flag=True)
@click.option("--prediction_intervals_length", type=int)
def cli(
    model: str,
    input_csv: TextIOWrapper,
    output_csv: TextIOWrapper,
    forecast_point: Optional[str],
    predictions_start_date: Optional[str],
    predictions_end_date: Optional[str],
    with_explanations: bool,
    prediction_intervals_length: int,
) -> None:
    """
    Command Line Interface main function.

    Parameters
    ----------
    model
    input_csv
    output_csv
    forecast_point
    predictions_start_date
    predictions_end_date
    with_explanations
    prediction_intervals_length
    """
    scoring_code_model = ScoringCodeModel(model)

    ts_type = (
        TimeSeriesType.HISTORICAL
        if (predictions_start_date or predictions_end_date)
        else TimeSeriesType.FORECAST
    )

    df = pd.read_csv(input_csv, dtype="str")
    start = time.time()
    result = scoring_code_model.predict(
        df,
        forecast_point=(isoparse(forecast_point) if forecast_point else None),
        predictions_start_date=(
            isoparse(predictions_start_date) if predictions_start_date else None
        ),
        predictions_end_date=(isoparse(predictions_end_date) if predictions_end_date else None),
        time_series_type=ts_type,
        max_explanations=(3 if with_explanations else 0),
        prediction_intervals_length=prediction_intervals_length,
    )
    print(f"Scoring took: {time.time() - start}")

    result.to_csv(output_csv, index=False, date_format="%Y-%m-%dT%H:%M:%S.%fZ")


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
