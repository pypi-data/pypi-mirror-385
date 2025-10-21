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
import contextvars
import datetime
import os
from io import BytesIO
from typing import Any, Dict, NamedTuple, Optional, Union, Set

import datarobot as dr
import pandas as pd
import pytz
from datarobot.client import get_client as get_dr_client
from datarobot.rest import RESTClientObject
from requests import Response
from requests.structures import CaseInsensitiveDict
import logging

from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter  # type: ignore
from urllib3 import Retry

from datarobot_predict import TimeSeriesType

logger = logging.getLogger(__name__)

REQUEST_LIMIT_BYTES = 50 * 1024 * 1024  # 50 MB
REQUEST_MAX_RETRY = int(os.environ.get("DATAROBOT_PREDICT_MAX_RETRY", "5"))
REQUEST_RETRYABLE_STATUS_CODES = {429, 570, 502, 503, 504}
REQUEST_RETRY_SLEEP = float(os.environ.get("DATAROBOT_PREDICT_RETRY_BACKOFF", "0.1"))


class PredictionResult(NamedTuple):
    """Predicion result type."""

    dataframe: pd.DataFrame
    """Result dataframe."""
    response_headers: CaseInsensitiveDict
    """Http response headers."""


class UnstructuredPredictionResult(NamedTuple):
    """Unstructured prediction result type."""

    data: Union[bytes, pd.DataFrame]
    """Raw response or DataFrame."""
    response_headers: CaseInsensitiveDict
    """Http response headers."""


class HttpClient(RESTClientObject):
    """
    A temporary class to add TCP keep-alive, once datarobot==3.7 will be published we
    can remove this class.
    """

    def __init__(self, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self._retry = Retry(
            total=REQUEST_MAX_RETRY,
            backoff_factor=REQUEST_RETRY_SLEEP,
            status_forcelist=REQUEST_RETRYABLE_STATUS_CODES,
            allowed_methods=False,
        )
        self._tcp_keepalive_time = 300
        self._tcp_keepalive_intvl = 60
        self._tcp_keepalive_probes = 3
        self.mount("http://", self._get_http_adapter())
        self.mount("https://", self._get_http_adapter())

    def _get_http_adapter(self) -> Any:
        return TCPKeepAliveAdapter(
            max_retries=self._retry,
            idle=self._tcp_keepalive_time,
            interval=self._tcp_keepalive_intvl,
            count=self._tcp_keepalive_probes,
        )


_http_client: contextvars.ContextVar[Optional[HttpClient]] = contextvars.ContextVar(
    "dr_http_client", default=None
)


def _initialize_http_client() -> HttpClient:
    dr_client = get_dr_client()
    return HttpClient(
        auth=dr_client.token,
        endpoint=dr_client.endpoint,
        connect_timeout=dr_client.connect_timeout,
        verify=dr_client.verify,
        authentication_type=dr_client.authentication_type,
    )


def get_client() -> HttpClient:
    http_client = _http_client.get()
    if http_client:
        return http_client
    http_client = _initialize_http_client()
    _http_client.set(http_client)
    return http_client


def clear_context() -> None:
    _http_client.set(None)


def predict(
    deployment: Union[dr.Deployment, str, None],
    data_frame: pd.DataFrame,
    max_explanations: Union[int, str] = 0,
    max_ngram_explanations: Optional[Union[int, str]] = None,
    threshold_high: Optional[float] = None,
    threshold_low: Optional[float] = None,
    time_series_type: TimeSeriesType = TimeSeriesType.FORECAST,
    forecast_point: Optional[datetime.datetime] = None,
    predictions_start_date: Optional[datetime.datetime] = None,
    predictions_end_date: Optional[datetime.datetime] = None,
    passthrough_columns: Union[str, Set[str], None] = None,
    explanation_algorithm: Optional[str] = None,
    prediction_endpoint: Optional[str] = None,
    timeout: int = 600,
) -> PredictionResult:
    """
    Get predictions using the DataRobot Prediction API.

    Parameters
    ----------
    deployment: Union[dr.Deployment, str, None]
        DataRobot deployment to use when computing predictions. Deployment can also be specified
        by deployment id or omitted which is used when prediction_endpoint is set, e.g. when
        using Portable Prediction Server.

        If dr.Deployment, the prediction server and deployment id will be taken from the deployment.
        If str, the argument is expected to be the deployment id.
        If None, no deployment id is used. This can be used for Portable Prediction Server
        single-model mode.
    data_frame: pd.DataFrame
        Input data.
    max_explanations: Union[int, str]
        Number of prediction explanations to compute.
        If 0 and 'explanation_algorithm' is set to 'xemp' (default), prediction explanations are disabled.
        If 0 and 'explanation_algorithm' is set to 'shap', all explanations will be computed.
        If "all", all explanations will be computed. This is only available for SHAP.
    max_ngram_explanations: Optional[Union[int, str]]
        The maximum number of text prediction explanations to supply per row of the dataset.
        The recommended `max_ngram_explanations` is `all` and by default is set to None.
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
    passthrough_columns: Union[str, Set[str], None]
        Columns from the input dataframe to include in with the output.
        If 'all', all input columns will be included.
        If None, no columns will be included.
    explanation_algorithm: Optional[str]
        Which algorithm will be used to calculate prediction explanations.
        If None, the default value will be used.
        Note: if 'max_explanations' is set to 0 or is missing, the response will contain
        - ALL explanation columns, when 'explanation_algorithm' is 'shap';
        - NO explanation columns, when 'explanation_algorithm' is 'xemp'.
    prediction_endpoint: Optional[str]
        Specific prediction endpoint to use. This overrides any prediction server found in
        deployment.
        If None, prediction endpoint found in deployment will be used.
    timeout: int
        Request timeout in seconds.

    Returns
    -------
    PredictionResult
        Prediction result consisting of a dataframe and response headers.

    """

    params: Dict[str, Any] = {
        "maxExplanations": max_explanations,
        "thresholdHigh": threshold_high,
        "thresholdLow": threshold_low,
    }
    if max_ngram_explanations is not None:
        params["maxNgramExplanations"] = max_ngram_explanations

    if threshold_high is not None:
        params["thresholdHigh"] = threshold_high

    if threshold_low is not None:
        params["thresholdLow"] = threshold_low

    if passthrough_columns == "all":
        params["passthroughColumnsSet"] = "all"
    elif passthrough_columns is not None:
        params["passthroughColumns"] = list(passthrough_columns)

    if explanation_algorithm is not None:
        params["explanationAlgorithm"] = explanation_algorithm

    if time_series_type == TimeSeriesType.FORECAST:
        if forecast_point is not None:
            params["forecastPoint"] = forecast_point.isoformat()
    else:
        if predictions_start_date is not None:
            params["predictionsStartDate"] = predictions_start_date.replace(
                tzinfo=pytz.utc
            ).isoformat()
        else:
            # Timestamps earlier then 1900 are not supported:
            # https://github.com/datarobot/DataRobot/blob/1a0004e4a982f9f4de047b18deabd5854683b9f3/common/entities/datetime_validators.py#L66
            params["predictionsStartDate"] = "1900-01-01T00:00:00.000000Z"

        if predictions_end_date is not None:
            params["predictionsEndDate"] = predictions_end_date.replace(tzinfo=pytz.utc).isoformat()
        else:
            # On DataRobot side timestamps are represented as pandas timestamp with nanosecond
            # precision which means that max supported value is
            # pd.Timestamp.max == "2262-04-11 23:47:16.854775807". I set nanoseconds to 0 to avoid
            # that rounding up on DataRobot side will make the value exceed allowed range.
            params["predictionsEndDate"] = pd.Timestamp.max.replace(  # type: ignore
                nanosecond=0, tzinfo=pytz.utc
            ).isoformat()

    headers: Dict[str, str] = {}

    response = _deployment_predict(
        deployment,
        "predictions",
        headers,
        params,
        data_frame,
        stream=False,
        timeout=timeout,
        prediction_endpoint=prediction_endpoint,
    )

    return PredictionResult(_read_response_csv(response), response.headers)


def predict_unstructured(
    deployment: dr.Deployment,
    data: Any,
    content_type: Optional[str] = None,
    accept: Optional[str] = None,
    timeout: int = 600,
) -> UnstructuredPredictionResult:
    """
    Get predictions for an unstructured model deployment.

    Parameters
    ----------
    deployment: dr.Deployment
        Deployment used to compute predictions.
    data: Any
        Data to send to the endpoint. This can be text, bytes or a file-like object. Anything
        that the python requests library accepts as data can be used.
        If pandas.DataFrame, it will be converted to csv and the response will also be converted
        to DataFrame if the response content-type is text/csv.
    content_type: str
        The content type for the data.
        If None, content type will be inferred from data.
    accept: Optional[str]
        The mimetypes supported for the return value.
        If None, any mimetype is supported.
    timeout: int
        Request timeout in seconds.

    Returns
    -------
    UnstructuredPredictionResult
        Prediction result consisting of raw response content and response headers.
    """

    headers = {}

    if content_type is not None:
        headers["Content-Type"] = content_type

    if accept is not None:
        # When RAPTOR-10424 is fixed, we can allow setting Accept header for unstructured
        raise ValueError("Setting Accept header is currently not supported")
    else:
        headers["Accept"] = ""

    response = _deployment_predict(
        deployment,
        "predictionsUnstructured",
        headers,
        params={},
        data=data,
        stream=False,
        timeout=timeout,
        prediction_endpoint=None,
    )

    if isinstance(data, pd.DataFrame) and response.headers["Content-Type"].lower().startswith(
        "text/csv"
    ):
        return UnstructuredPredictionResult(_read_response_csv(response), response.headers)

    return UnstructuredPredictionResult(response.content, response.headers)


def _deployment_predict(
    deployment: Union[dr.Deployment, str, None],
    endpoint: str,
    headers: Dict[str, str],
    params: Dict[str, Any],
    data: Any,
    stream: bool,
    timeout: int,
    prediction_endpoint: Optional[str],
) -> Response:
    headers = headers.copy()

    if not prediction_endpoint:
        if not isinstance(deployment, dr.Deployment):
            raise ValueError("Can't infer prediction endpoint without Deployment instance.")

        if _is_serverless_deployment(deployment):
            # on serverless deployments, the endpoint is different than the regular prediction instances.
            # regardless if the deployment is unstructured or not, all requests go to /predictions
            url = f"{get_client().endpoint}/deployments/{deployment.id}/{endpoint}"
            headers["Authorization"] = f"Bearer {get_client().token}"
        elif "datarobot-nginx" in os.environ.get("DATAROBOT_ENDPOINT", ""):
            # This is a case for on-prem and ST SAAS installs
            url = f"http://datarobot-prediction-server:80/predApi/v1.0/deployments/{deployment.id}/{endpoint}"
        else:
            pred_server = deployment.default_prediction_server
            if not pred_server:
                raise ValueError(
                    "Can't make prediction request because Deployment object doesn't contain "
                    "default prediction server"
                )
            dr_key = pred_server.get("datarobot-key")
            if dr_key:
                headers["datarobot-key"] = dr_key

            url = f"{pred_server['url']}/predApi/v1.0/deployments/{deployment.id}/{endpoint}"

    else:
        url = f"{prediction_endpoint}"
        deployment_id = deployment.id if isinstance(deployment, dr.Deployment) else deployment
        if deployment_id:
            url += f"/deployments/{deployment_id}"
        url += f"/{endpoint}"

    if isinstance(data, pd.DataFrame):
        if "Content-Type" not in headers:
            headers["Content-Type"] = "text/csv"
        elif headers["Content-Type"] != "text/csv":
            raise ValueError(f"Expected test/csv content-type, got {headers['Content-Type']}")

        if "Accept" not in headers:
            headers["Accept"] = "text/csv"

        csv = data.to_csv(index=False)
        assert csv is not None
        data = csv.encode()
        if len(data) > REQUEST_LIMIT_BYTES:
            raise ValueError(
                f"DataFrame converted to csv exceeds 50MB request limit. "
                f"DataFrame size: {len(data)} bytes"
            )

    return get_client().request(
        "POST",
        url,
        params=params,
        data=data,
        headers=headers,
        stream=stream,
        timeout=timeout,
    )


def _read_response_csv(response: Response) -> pd.DataFrame:
    return pd.read_csv(BytesIO(response.content))


def _is_serverless_deployment(deployment: dr.Deployment) -> bool:
    """Check if deployment is deployed on a `datarobot_serverless` platform type"""
    if not deployment.prediction_environment:
        return False

    if deployment.prediction_environment.get("platform") == "datarobotServerless":
        return True

    return False
