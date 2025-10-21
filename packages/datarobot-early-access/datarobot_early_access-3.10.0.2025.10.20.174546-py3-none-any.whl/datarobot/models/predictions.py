#
# Copyright 2021-2025 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from datetime import datetime
from io import StringIO
from typing import TYPE_CHECKING, Any, List, Optional, Union, cast
from urllib.parse import urlencode

import pandas as pd
import trafaret as t

from datarobot import enums, errors
from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import from_api, parse_time, raw_prediction_response_to_dataframe

_base_metadata_path = "projects/{project_id}/predictionsMetadata/"
_get_metadata_path = _base_metadata_path + "{prediction_id}/"
# get predictions for particular prediction id.
_get_path = "projects/{project_id}/predictions/{prediction_id}/"

if TYPE_CHECKING:
    from datarobot._compat import TypedDict
    from datarobot.models.api_object import ServerDataDictType

    class ShapWarnings(TypedDict):
        mismatch_row_count: int
        max_normalized_mismatch: float

    class PredictionAsDict(TypedDict):  # pylint: disable=missing-class-docstring
        id: str
        model_id: str
        prediction_dataset_id: Optional[str]
        dataset_id: Optional[str]
        includes_prediction_intervals: bool
        prediction_intervals_size: Optional[int]
        forecast_point: Optional[datetime]
        predictions_start_date: Optional[datetime]
        predictions_end_date: Optional[datetime]
        actual_value_column: Optional[str]
        explanation_algorithm: Optional[str]
        max_explanations: Optional[int]
        shap_warnings: Optional[ShapWarnings]

    class PredictionsResponse(TypedDict):
        predictions: PredictionAsDict
        task: Any  # TODO - Annotate this better
        shapBaseValue: List[float]


class Predictions(APIObject):
    """
    Represents predictions metadata and provides access to prediction results.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model
    prediction_id : str
        id of generated predictions
    includes_prediction_intervals : Optional[bool]
        (New in v2.16) For :ref:`time series <time-series>` projects only.
        Indicates if prediction intervals will be part of the response. Defaults to False.
    prediction_intervals_size : Optional[int]
        (New in v2.16) For :ref:`time series <time-series>` projects only.
        Indicates the percentile used for prediction intervals calculation. Will be present only
        if `includes_prediction_intervals` is True.
    forecast_point : datetime.datetime, optional
        (New in v2.20) For :ref:`time series <time-series>` projects only. This is the default point
        relative to which predictions will be generated, based on the forecast window of the
        project. See the time series :ref:`prediction documentation <time-series-predict>` for more
        information.
    predictions_start_date : datetime.datetime or None, optional
        (New in v2.20) For :ref:`time series <time-series>` projects only. The start date for bulk
        predictions. Note that this parameter is for generating historical predictions using the
        training data. This parameter should be provided in conjunction with
        ``predictions_end_date``. Can't be provided with the ``forecast_point`` parameter.
    predictions_end_date : datetime.datetime or None, optional
        (New in v2.20) For :ref:`time series <time-series>` projects only. The end date for bulk
        predictions, exclusive. Note that this parameter is for generating historical predictions
        using the training data. This parameter should be provided in conjunction with
        ``predictions_start_date``. Can't be provided with the ``forecast_point`` parameter.
    actual_value_column : string, optional
        (New in version v2.21) For :ref:`time series <time-series>` unsupervised projects only.
        Actual value column which was used to calculate the classification metrics and
        insights on the prediction dataset. Can't be provided with the ``forecast_point``
        parameter.
    explanation_algorithm : datarobot.enums.EXPLANATIONS_ALGORITHM, optional
        (New in version v2.21) If set to 'shap', the response will include prediction
        explanations based on the SHAP explainer (SHapley Additive exPlanations). Defaults to null
        (no prediction explanations).
    max_explanations : Optional[int]
        (New in version v2.21) The maximum number of explanation values that should be returned
        for each row, ordered by absolute value, greatest to least. If null, no limit. In the case
        of 'shap': if the number of features is greater than the limit, the sum of remaining values
        will also be returned as `shapRemainingTotal`. Defaults to null. Cannot be set if
        `explanation_algorithm` is omitted.
    shap_warnings : dict, optional
        (New in version v2.21) Will be present if `explanation_algorithm` was set to
        `datarobot.enums.EXPLANATIONS_ALGORITHM.SHAP` and there were additivity failures during SHAP
        values calculation.


    Examples
    --------

    List all predictions for a project

    .. code-block:: python

        import datarobot as dr

        # Fetch all predictions for a project
        all_predictions = dr.Predictions.list(project_id)

        # Inspect all calculated predictions
        for predictions in all_predictions:
            print(predictions)  # repr includes project_id, model_id, and dataset_id

    Retrieve predictions by id

    .. code-block:: python

        import datarobot as dr

        # Getting predictions by id
        predictions = dr.Predictions.get(project_id, prediction_id)

        # Dump actual predictions
        df = predictions.get_all_as_dataframe()
        print(df)
    """

    def __init__(
        self,
        project_id: str,
        prediction_id: str,
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        includes_prediction_intervals: Optional[bool] = None,
        prediction_intervals_size: Optional[int] = None,
        forecast_point: Optional[datetime] = None,
        predictions_start_date: Optional[datetime] = None,
        predictions_end_date: Optional[datetime] = None,
        actual_value_column: Optional[str] = None,
        explanation_algorithm: Optional[str] = None,
        max_explanations: Optional[int] = None,
        shap_warnings: Optional[ShapWarnings] = None,
    ) -> None:
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.prediction_id = prediction_id
        self.path = _get_path.format(project_id=self.project_id, prediction_id=self.prediction_id)
        self.includes_prediction_intervals = includes_prediction_intervals
        self.prediction_intervals_size = prediction_intervals_size
        self.forecast_point = forecast_point
        self.predictions_start_date = predictions_start_date
        self.predictions_end_date = predictions_end_date
        self.actual_value_column = actual_value_column
        self.explanation_algorithm = explanation_algorithm
        self.max_explanations = max_explanations
        self.shap_warnings = shap_warnings

    _metadata_trafaret = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("url"): String(),
            t.Key("model_id"): String(),
            t.Key("prediction_dataset_id"): String(),
            t.Key("includes_prediction_intervals"): t.Bool(),
            t.Key("prediction_intervals_size", optional=True): Int(),
            t.Key("forecast_point", optional=True): parse_time,
            t.Key("predictions_start_date", optional=True): parse_time,
            t.Key("predictions_end_date", optional=True): parse_time,
            t.Key("actual_value_column", optional=True): String(),
            t.Key("explanation_algorithm", optional=True): String(),
            t.Key("max_explanations", optional=True): Int(),
            t.Key("shap_warnings", optional=True): t.Dict(
                {t.Key("mismatch_row_count"): Int(), t.Key("max_normalized_mismatch"): t.Float()}
            ),
        }
    ).ignore_extra("*")

    @classmethod
    def _build_list_path(  # pylint: disable=missing-function-docstring
        cls, project_id: str, model_id: Optional[str] = None, dataset_id: Optional[str] = None
    ) -> str:
        args = {}
        if model_id:
            args["modelId"] = model_id
        if dataset_id:
            args["predictionDatasetId"] = dataset_id

        path = _base_metadata_path.format(project_id=project_id)
        if args:
            path = f"{path}?{urlencode(args)}"

        return path

    @classmethod
    def _from_server_object(  # pylint: disable=missing-function-docstring
        cls,
        project_id: str,
        item: PredictionAsDict,
    ) -> Predictions:
        pred = cls(
            project_id,
            prediction_id=item["id"],
            model_id=item["model_id"],
            dataset_id=item.get("prediction_dataset_id") or item.get("dataset_id"),
            includes_prediction_intervals=item["includes_prediction_intervals"],
        )
        if pred.includes_prediction_intervals:
            pred.prediction_intervals_size = item["prediction_intervals_size"]
        if item.get("forecast_point"):
            pred.forecast_point = item["forecast_point"]
        if item.get("predictions_start_date"):
            pred.predictions_start_date = item["predictions_start_date"]
        if item.get("predictions_end_date"):
            pred.predictions_end_date = item["predictions_end_date"]
        if item.get("actual_value_column"):
            pred.actual_value_column = item["actual_value_column"]
        if item.get("explanation_algorithm"):
            pred.explanation_algorithm = item["explanation_algorithm"]
        if item.get("max_explanations"):
            pred.max_explanations = item["max_explanations"]
        if item.get("shap_warnings"):
            pred.shap_warnings = item["shap_warnings"]

        return pred

    @classmethod
    def list(
        cls, project_id: str, model_id: Optional[str] = None, dataset_id: Optional[str] = None
    ) -> List[Predictions]:
        """
        Fetch all the computed predictions metadata for a project.

        Parameters
        ----------
        project_id : str
            id of the project
        model_id : Optional[str]
            if specified, only predictions metadata for this model will be retrieved
        dataset_id : Optional[str]
            if specified, only predictions metadata for this dataset will be retrieved

        Returns
        -------
        A list of :py:class:`Predictions <datarobot.models.Predictions>` objects
        """
        path = cls._build_list_path(project_id, model_id=model_id, dataset_id=dataset_id)
        converted = from_api(cls._server_data(path))
        retval = []
        for item in cast("ServerDataDictType", converted)["data"]:
            validated = cls._metadata_trafaret.check(item)
            pred = cls._from_server_object(project_id, validated)
            retval.append(pred)
        return retval

    @classmethod
    def get(cls, project_id: str, prediction_id: str) -> Predictions:
        """
        Retrieve the specific predictions metadata

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        prediction_id : str
            id of the prediction set

        Returns
        -------
        :py:class:`Predictions <datarobot.models.Predictions>` object representing specified
        predictions
        """
        path = _get_metadata_path.format(project_id=project_id, prediction_id=prediction_id)

        converted = from_api(cls._server_data(path))
        validated = cls._metadata_trafaret.check(converted)

        return cls._from_server_object(project_id, validated)

    def get_all_as_dataframe(
        self, class_prefix: str = enums.PREDICTION_PREFIX.DEFAULT, serializer: str = "json"
    ) -> pd.DataFrame:
        """
        Retrieve all prediction rows and return them as a pandas.DataFrame.

        Parameters
        ----------
        class_prefix : Optional[str]
            The prefix to append to labels in the final dataframe. Default is ``class_``
            (e.g., apple -> class_apple)
        serializer : Optional[str]
            Serializer to use for the download. Options: ``json`` (default) or ``csv``.

        Returns
        -------
        dataframe: pandas.DataFrame

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        serializers = {
            "json": self._get_all_as_dataframe_json,
            "csv": self._get_all_as_dataframe_csv,
        }
        if serializer not in serializers:
            raise ValueError(f'Unknown serializer "{serializer}", use "json" or "csv"')

        return serializers[serializer](class_prefix)

    def _get_all_as_dataframe_json(self, class_prefix: str) -> pd.DataFrame:
        data = self._server_data(self.path)
        return raw_prediction_response_to_dataframe(cast("PredictionsResponse", data), class_prefix)

    def _get_all_as_dataframe_csv(
        self,
        class_prefix: str,  # pylint: disable=unused-argument
    ) -> pd.DataFrame:
        resp = self._client.get(self.path, headers={"Accept": "text/csv"}, stream=True)
        if resp.status_code == 200:
            content = resp.content.decode("utf-8")
            return pd.read_csv(StringIO(content), encoding="utf-8")
        else:
            raise errors.ServerError(
                f"Server returned unknown status code: {resp.status_code}",
                resp.status_code,
            )

    def download_to_csv(
        self, filename: Union[str, bool], encoding: str = "utf-8", serializer: str = "json"
    ) -> None:
        """
        Save prediction rows into CSV file.

        Parameters
        ----------
        filename : str or file object
            path or file object to save prediction rows
        encoding : string, optional
            A string representing the encoding to use in the output file, defaults to
            'utf-8'
        serializer : Optional[str]
            Serializer to use for the download. Options: ``json`` (default) or ``csv``.
        """
        df = self.get_all_as_dataframe(serializer=serializer)
        df.to_csv(
            path_or_buf=filename,
            header=True,
            index=False,
            encoding=encoding,
        )

    def __repr__(self) -> str:
        template = (
            "{}(prediction_id={!r}, project_id={!r}, model_id={!r}, dataset_id={!r}, "
            "includes_prediction_intervals={!r}, prediction_intervals_size={!r}, "
            "forecast_point={!r}, predictions_start_date={!r}, "
            "predictions_end_date={!r}, actual_value_column={!r}, "
            "explanation_algorithm={!r}, max_explanations={!r}, shap_warnings={!r})"
        )
        return template.format(
            type(self).__name__,
            self.prediction_id,
            self.project_id,
            self.model_id,
            self.dataset_id,
            self.includes_prediction_intervals,
            self.prediction_intervals_size,
            self.forecast_point,
            self.predictions_start_date,
            self.predictions_end_date,
            self.actual_value_column,
            self.explanation_algorithm,
            self.max_explanations,
            self.shap_warnings,
        )
