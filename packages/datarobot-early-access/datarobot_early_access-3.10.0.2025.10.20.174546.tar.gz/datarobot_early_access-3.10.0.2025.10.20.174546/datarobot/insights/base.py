#
# Copyright 2024-2025 DataRobot, Inc. and its affiliates.
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

from io import StringIO
from typing import Any, Dict, Iterable, List, Optional, Union, cast

import pandas as pd
import trafaret as t
from typing_extensions import Self

from datarobot.enums import DEFAULT_MAX_WAIT, ENTITY_TYPES, INSIGHTS_SOURCES
from datarobot.mixins.browser_mixin import BrowserMixin
from datarobot.mixins.datarobot_ui_mixin import DatarobotUIMixin
from datarobot.models import StatusCheckJob
from datarobot.models.api_object import APIObject
from datarobot.utils import pagination

DATAROBOT_INSIGHTS_FEATURE_IMPACT_MIMETYPE = "application/vnd.datarobot.insight.feature-impact"


class BaseInsight(APIObject, BrowserMixin, DatarobotUIMixin):
    """Base Insight class for modern insights

    This class serves as a template for modern insights created using the Root Insights framework.
    It provides most necessary functions for easily implementing classes that wrap specific insights.

    """

    # To use this class it should be inherited and the `INSIGHT_NAME` and `INSIGHT_DATA` attributes
    # should be replaced with the correct values.
    #
    # Example:
    # You have an insight that has the endpoint `insights/myInsight` and the insight's calculator
    # produces a response that contains a boolean field called `insight_worked` and a list of
    # string values called `insight_values`.
    #
    # To make things easier for the user you may want to add some easily accessible properties
    # to allow them to quickly get the values of the insight.
    #
    # Example insight result:
    #
    # .. code-block:: text
    #
    #         {
    #             "insight_worked": true,
    #             "insight_values": ["hello", "world"]
    #         }
    #
    # You can simply create a wrapper for this new insight using this framework:
    #
    # .. code-block:: python
    #
    #         class MyInsight(BaseInsight):
    #             INSIGHT_NAME = "myInsight"
    #             INSIGHT_DATA = {
    #                 t.Key("insight_worked"): t.Bool(),
    #                 t.Key("insight_values"): t.List(t.String()),
    #             }
    #
    #             @property
    #             def values() -> List[str]:
    #                 return cast(List[str], self.data["insight_values"])
    #
    # All of the computation and insight retrieval handling will be accounted for by the base insight.
    # This class can also be overridden for more complex queries by adjusting the functionality of the
    # `_get_payload` function to provide additional required options, but most insights won't need
    # this capability.

    INSIGHT_NAME: str = "base"  # Defined by subclasses to identify the formal name for endpoints
    INSIGHT_DATA = t.Any()  # Defined by subclasses for specific insights

    _converter = t.Dict(
        {
            t.Key("id"): t.String(),
            t.Key("entity_id"): t.String(),
            t.Key("project_id"): t.String(),
            t.Key("source"): t.String(),
            t.Key("data_slice_id", optional=True): t.Or(t.String(), t.Null()),
            t.Key("external_dataset_id", optional=True): t.Or(t.String(), t.Null()),
            t.Key("data"): INSIGHT_DATA,
        }
    ).ignore_extra("*")

    # all feature impact types are rendered with the same UI components mapped with this mime type
    _datarobot_ui_mime_type = DATAROBOT_INSIGHTS_FEATURE_IMPACT_MIMETYPE

    def __init__(
        self,
        id: str,
        entity_id: str,
        project_id: str,
        source: str,
        data: Any,
        data_slice_id: Optional[str] = None,
        external_dataset_id: Optional[str] = None,
    ):
        """Base Insight class

        Parameters
        ----------
        id: str
            ID of the insight.
        entity_id: str
            ID of the entity associated with the insight.
        project_id: str
            ID of the project associated with the insight.
        source: str
            Source type of the insight.
        data: Dict
            Results of the computed insight.
        data_slice_id: Optional[str]
            Data slice ID associated with the insight.
        external_dataset_id: Optional[str]
            External dataset ID associated with the insight.
        """
        self.id = id
        self.entity_id = entity_id
        self.project_id = project_id
        self.source = source
        self.data_slice_id = data_slice_id
        self.external_dataset_id = external_dataset_id

        self.data = data

    @classmethod
    def _compute_url(cls) -> str:
        """Construct a compute url"""
        return f"insights/{cls.INSIGHT_NAME}/"

    @classmethod
    def _retrieve_url(cls) -> str:
        """Construct a retrieve url"""
        return f"insights/{cls.INSIGHT_NAME}" + "/models/{}/"

    def get_uri(self) -> str:
        """This should define the URI to their browser based interactions"""
        raise NotImplementedError

    def sort(self, key_name: str) -> None:
        """Sorts insights data"""
        raise NotImplementedError

    @classmethod
    def from_server_data(
        cls,
        data: Dict[str, Any],  # type: ignore[override]
        keep_attrs: Optional[Iterable[str]] = None,
    ) -> Self:
        """Override from_server_data to handle paginated responses"""
        if all(attrib in data for attrib in ["count", "next", "previous"]):
            # If true, the data response is a paginated response from a compute command and the data
            # entity should be unwrapped. There should only be one response.
            data = data["data"][0]

        return super().from_server_data(data=data, keep_attrs=keep_attrs)

    @classmethod
    def _get_payload(
        cls,
        entity_id: str,
        source: str = INSIGHTS_SOURCES.VALIDATION,
        data_slice_id: Optional[str] = None,
        external_dataset_id: Optional[str] = None,
        entity_type: Optional[ENTITY_TYPES] = None,
        quick_compute: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Union[str, int, bool]]:
        """Construct a payload for a compute request. May be overridden by insight subclasses to
        accept additional parameters.
        """
        _ = kwargs
        payload: Dict[str, Union[str, bool]] = {
            "entityId": entity_id,
            "source": source,
        }
        if data_slice_id is not None:
            payload["dataSliceId"] = data_slice_id
        if external_dataset_id is not None:
            payload["externalDatasetId"] = external_dataset_id
        if entity_type is not None:
            payload["entityType"] = entity_type
        if quick_compute is not None:
            payload["quickCompute"] = quick_compute

        return cast(Dict[str, Union[str, int, bool]], payload)

    @classmethod
    def compute(
        cls,
        entity_id: str,
        source: str = INSIGHTS_SOURCES.VALIDATION,
        data_slice_id: Optional[str] = None,
        external_dataset_id: Optional[str] = None,
        entity_type: Optional[ENTITY_TYPES] = ENTITY_TYPES.DATAROBOT_MODEL,
        quick_compute: Optional[bool] = None,
        **kwargs: Any,
    ) -> StatusCheckJob:
        """Submit an insight compute request. You can use `create` if you want to
        wait synchronously for the completion of the job. May be overridden by insight subclasses to
        accept additional parameters.

        Parameters
        ----------
        entity_id: str
            The ID of the entity to compute the insight.
        source: str
            The source type to use when computing the insight.
        data_slice_id: Optional[str]
            Data slice ID to use when computing the insight.
        external_dataset_id: Optional[str]
            External dataset ID to use when computing the insight.
        entity_type: Optional[ENTITY_TYPES]
            The type of the entity associated with the insight. Select one of the ENTITY_TYPE enum
            values, or accept the default, "datarobotModel".
        quick_compute: Optional[bool]
            Sets whether to use quick-compute for the insight. If `True` or unspecified, the insight
            is computed using a 2500-row data sample. If `False`, the insight is computed using all
            rows in the chosen source.

        Returns
        -------
        StatusCheckJob
            Status check job entity for the asynchronous insight calculation.
        """
        payload = cls._get_payload(
            entity_id=entity_id,
            source=source,
            data_slice_id=data_slice_id,
            external_dataset_id=external_dataset_id,
            entity_type=entity_type,
            quick_compute=quick_compute,
            **kwargs,
        )
        response = cls._client.post(cls._compute_url(), data=payload)

        return StatusCheckJob.from_response(response, cls)

    @classmethod
    def create(
        cls,
        entity_id: str,
        source: str = INSIGHTS_SOURCES.VALIDATION,
        data_slice_id: Optional[str] = None,
        external_dataset_id: Optional[str] = None,
        entity_type: Optional[ENTITY_TYPES] = ENTITY_TYPES.DATAROBOT_MODEL,
        quick_compute: Optional[bool] = None,
        max_wait: Optional[int] = DEFAULT_MAX_WAIT,
        **kwargs: Any,
    ) -> Self:
        """Create an insight and wait for completion. May be overridden by insight subclasses to
        accept additional parameters.

        Parameters
        ----------
        entity_id: str
            The ID of the entity to compute the insight.
        source: str
            The source type to use when computing the insight.
        data_slice_id: Optional[str]
            Data slice ID to use when computing the insight.
        external_dataset_id: Optional[str]
            External dataset ID to use when computing the insight.
        entity_type: Optional[ENTITY_TYPES]
            The type of the entity associated with the insight. Select one of the ENTITY_TYPE enum
            values, or accept the default, "datarobotModel".
        quick_compute: Optional[bool]
            Sets whether to use quick-compute for the insight. If `True` or unspecified, the insight
            is computed using a 2500-row data sample. If `False`, the insight is computed using all
            rows in the chosen source.
        max_wait: int
            The number of seconds to wait for the result.

        Returns
        -------
        Self
            Entity of the newly or already computed insights.
        """
        status_check_job = cls.compute(
            entity_id=entity_id,
            source=source,
            data_slice_id=data_slice_id,
            external_dataset_id=external_dataset_id,
            entity_type=entity_type,
            quick_compute=quick_compute,
            **kwargs,
        )
        return cast(Self, status_check_job.get_result_when_complete(max_wait=cast(int, max_wait)))

    @classmethod
    def list(cls, entity_id: str) -> List[Self]:
        """List all generated insights.

        Parameters
        ----------
        entity_id: str
            The ID of the entity queried for listing all generated insights.

        Returns
        -------
        List[Self]
            List of newly or previously computed insights.
        """
        url = cls._retrieve_url().format(entity_id)
        return [cls.from_server_data(x) for x in pagination.unpaginate(url, {}, cls._client)]

    @classmethod
    def get(
        cls,
        entity_id: str,
        source: str = INSIGHTS_SOURCES.VALIDATION,
        quick_compute: Optional[bool] = None,
        **kwargs: Any,
    ) -> Self:
        """Return the first matching insight based on the entity id and kwargs.

        Parameters
        ----------
        entity_id: str
            The ID of the entity to retrieve generated insights.
        source: str
            The source type to use when retrieving the insight.
        quick_compute: Optional[bool]
            Sets whether to retrieve the insight that was computed using quick-compute. If not
            specified, quick_compute is not used for matching.

        Returns
        -------
        Self
            Previously computed insight.
        """
        url = cls._retrieve_url().format(entity_id)
        query_params: Dict[str, Union[str, bool]] = {"source": source, **kwargs}
        if quick_compute is not None:
            query_params["quickCompute"] = quick_compute
        return [
            cls.from_server_data(x) for x in pagination.unpaginate(url, query_params, cls._client)
        ][0]


class CsvSupportedInsight(BaseInsight):
    """Base Insight class for insights that support CSV export

    This class serves as a template for insights that support CSV export. It provides additional
    functionality to export the insight results to a CSV file.

    """

    CSV_HEADERS = {"Content-Type": "text/csv", "Accept": "text/csv"}

    @classmethod
    def get_as_csv(cls, entity_id: str, **kwargs: Any) -> str:
        """Retrieve a specific insight represented in CSV format.

        Parameters
        ----------
        entity_id: str
            ID of the entity to retrieve the insight.
        **kwargs: Any
            Additional keyword arguments to pass to the retrieve function.

        Returns
        -------
        str
            The retrieved insight.
        """
        url = cls._retrieve_url().format(entity_id)
        resp_data = cls._client.get(url, params=kwargs, headers=cls.CSV_HEADERS)
        return cast(str, resp_data.text)

    @classmethod
    def get_as_dataframe(cls, entity_id: str, **kwargs: Any) -> pd.DataFrame:
        """Retrieve a specific insight represented as a pandas DataFrame.

        Parameters
        ----------
        entity_id: str
            ID of the entity to retrieve the insight.
        **kwargs: Any
            Additional keyword arguments to pass to the retrieve function.

        Returns
        -------
        DataFrame
            The retrieved insight.
        """
        csv_data = cls.get_as_csv(entity_id, **kwargs)
        return pd.read_csv(StringIO(csv_data))
