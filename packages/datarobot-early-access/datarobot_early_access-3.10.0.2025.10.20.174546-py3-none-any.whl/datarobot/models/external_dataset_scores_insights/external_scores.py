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

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import trafaret as t

from datarobot._compat import String
from datarobot.errors import ClientError
from datarobot.utils import get_id_from_response
from datarobot.utils.pagination import unpaginate

from ..api_object import APIObject

if TYPE_CHECKING:
    from datarobot._compat import TypedDict
    from datarobot.models import Job

    class Score(TypedDict):
        label: str
        value: float


DEFAULT_BATCH_SIZE = 100


class ExternalScores(APIObject):
    """Metric scores on prediction dataset with target or actual value column in unsupervised
    case. Contains project metrics for supervised and special classification metrics set for
    unsupervised projects.

    .. versionadded:: v2.21

    Attributes
    ----------
    project_id: str
        id of the project the model belongs to
    model_id: str
        id of the model
    dataset_id: str
        id of the prediction dataset with target or actual value column for unsupervised case
    actual_value_column: Optional[str]
        For unsupervised projects only.
        Actual value column which was used to calculate the classification metrics and
        insights on the prediction dataset.
    scores: list of dicts in a form of {'label': metric_name, 'value': score}
        Scores on the dataset.


    Examples
    --------

    List all scores for a dataset

    .. code-block:: python

        from datarobot.models.external_dataset_scores_insights.external_scores import ExternalScores
        scores = ExternalScores.list(project_id, dataset_id=dataset_id)

    """

    _path = "projects/{project_id}/externalScores/"

    _converter = t.Dict(
        {
            t.Key("project_id"): String(),
            t.Key("model_id"): String(),
            t.Key("dataset_id"): String(),
            t.Key("actual_value_column", optional=True): t.Or(String(), t.Null()),
            t.Key("scores"): t.List(t.Dict({t.Key("label"): String(), t.Key("value"): t.Float()})),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id: str,
        scores: List[Score],
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        actual_value_column: Optional[str] = None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.actual_value_column = actual_value_column
        self.scores = scores

    @classmethod
    def create(
        cls,
        project_id: str,
        model_id: str,
        dataset_id: str,
        actual_value_column: Optional[str] = None,
    ) -> Job:
        """Compute an external dataset insights for the specified model.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which insights is requested
        dataset_id : str
            id of the dataset for which insights is requested
        actual_value_column : Optional[str]
            actual values column label, for unsupervised projects only


        Returns
        -------
        job : Job
            an instance of created async job
        """

        from datarobot.models import Job  # pylint: disable=import-outside-toplevel,cyclic-import

        payload = {"modelId": model_id, "datasetId": dataset_id}
        if actual_value_column:
            payload["actualValueColumn"] = actual_value_column
        url = cls._path.format(project_id=project_id)
        response = cls._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    @classmethod
    def list(
        cls,
        project_id: str,
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[ExternalScores]:
        """Fetch external scores list for the project and optionally for model and dataset.

        Parameters
        ----------
        project_id: str
            id of the project
        model_id: Optional[str]
            if specified, only scores for this model will be retrieved
        dataset_id: Optional[str]
            if specified, only scores for this dataset will be retrieved
        offset: Optional[int]
            this many results will be skipped, default: 0
        limit: Optional[int]
            at most this many results are returned, default: 100, max 1000.
            To return all results, specify 0

        Returns
        -------
            A list of :py:class:`External Scores <datarobot.ExternalScores>` objects

        """
        params: Dict[str, Union[str, int]] = {"limit": limit, "offset": offset}
        if model_id:
            params["modelId"] = model_id
        if dataset_id:
            params["datasetId"] = dataset_id

        url = cls._path.format(project_id=project_id)
        if limit == 0:  # unlimited results
            params["limit"] = DEFAULT_BATCH_SIZE
            return [cls.from_server_data(entry) for entry in unpaginate(url, params, cls._client)]
        r_data = cls._client.get(url, params=params).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, project_id: str, model_id: str, dataset_id: str) -> ExternalScores:
        """Retrieve external scores for the project, model and dataset.

        Parameters
        ----------
        project_id: str
            id of the project
        model_id: str
            if specified, only scores for this model will be retrieved
        dataset_id: str
            if specified, only scores for this dataset will be retrieved

        Returns
        -------
            :py:class:`External Scores <datarobot.ExternalScores>` object

        """
        if model_id is None:
            raise ValueError("model_id must be specified")
        if dataset_id is None:
            raise ValueError("dataset_id must be specified")
        scores = cls.list(project_id, model_id=model_id, dataset_id=dataset_id)
        if not scores:
            raise ClientError("Requested scores do not exist.", 404)
        return scores[0]

    def __repr__(self) -> str:
        return (
            "Scores(project_id={}, model_id={}, dataset_id={}, "
            "scores={}, actual_value_column={})"
        ).format(
            self.project_id,
            self.model_id,
            self.dataset_id,
            self.scores,
            self.actual_value_column,
        )
