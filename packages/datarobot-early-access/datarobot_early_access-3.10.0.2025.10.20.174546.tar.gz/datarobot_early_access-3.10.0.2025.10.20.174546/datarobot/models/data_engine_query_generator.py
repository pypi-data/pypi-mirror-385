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

from io import IOBase
from typing import Optional, Union

import pandas as pd
import trafaret as t

from datarobot._compat import String
from datarobot.enums import FileLocationType, LocalSourceType
from datarobot.errors import InvalidUsageError
from datarobot.models.api_object import APIObject
from datarobot.models.dataset import Dataset
from datarobot.models.project import PredictionDataset, Project
from datarobot.utils.source import parse_source_type

from ..enums import DEFAULT_MAX_WAIT
from ..utils.waiters import wait_for_async_resolution


class DataEngineQueryGenerator(APIObject):
    """DataEngineQueryGenerator is used to set up time series data prep.

    .. versionadded:: v2.27

    Attributes
    ----------
    id: str
        id of the query generator
    query: str
        text of the generated Spark SQL query
    datasets: list(QueryGeneratorDataset)
        datasets associated with the query generator
    generator_settings: QueryGeneratorSettings
        the settings used to define the query
    generator_type: str
        "TimeSeries" is the only supported type
    """

    _path = "dataEngineQueryGenerators/"
    _converter = t.Dict(
        {
            t.Key("datasets", optional=True): t.List(
                t.Dict(
                    {
                        t.Key("alias"): String,
                        t.Key("dataset_id"): String,
                        t.Key("dataset_version_id", optional=True): String,
                    }
                )
            ),
            t.Key("generator_settings"): t.Dict(
                {
                    t.Key("datetime_partition_column"): String,
                    t.Key("time_unit"): String,
                    t.Key("time_step"): t.Int,
                    t.Key("default_numeric_aggregation_method"): String,
                    t.Key("default_categorical_aggregation_method"): String,
                    t.Key("target", optional=True): String,
                    t.Key("multiseries_id_columns", optional=True): t.List(String),
                    t.Key("default_text_aggregation_method", optional=True): String,
                    t.Key("start_from_series_min_datetime", optional=True): t.Bool,
                    t.Key("end_to_series_max_datetime", optional=True): t.Bool,
                }
            ).allow_extra("*"),
            t.Key("generator_type"): String,
            t.Key("id"): String,
            t.Key("query"): String,
        }
    ).allow_extra("*")

    def __init__(self, **generator_kwargs):
        self.datasets = generator_kwargs["datasets"]
        self.generator_type = generator_kwargs["generator_type"]
        self.generator_settings = generator_kwargs["generator_settings"]
        self.id = generator_kwargs["id"]
        self.query = generator_kwargs["query"]

    def __repr__(self):
        return (
            "{}(generator_id={}, datasets={}, generator_type={}, " "generator_settings={}, query={}"
        ).format(
            self.__class__.__name__,
            self.id,
            self.datasets,
            self.generator_type,
            self.generator_settings,
            self.query,
        )

    @classmethod
    def create(cls, generator_type, datasets, generator_settings):
        """Creates a query generator entity.

        .. versionadded:: v2.27

        Parameters
        ----------
        generator_type : str
            Type of data engine query generator
        datasets : List[QueryGeneratorDataset]
            Source datasets in the Data Engine workspace.
        generator_settings : dict
            Data engine generator settings of the given `generator_type`.

        Returns
        -------
        query_generator : DataEngineQueryGenerator
            The created generator

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            from datarobot.models.data_engine_query_generator import (
               QueryGeneratorDataset,
               QueryGeneratorSettings,
            )
            dataset = QueryGeneratorDataset(
               alias='My_Awesome_Dataset_csv',
               dataset_id='61093144cabd630828bca321',
               dataset_version_id=1,
            )
            settings = QueryGeneratorSettings(
               datetime_partition_column='date',
               time_unit='DAY',
               time_step=1,
               default_numeric_aggregation_method='sum',
               default_categorical_aggregation_method='mostFrequent',
            )
            g = dr.DataEngineQueryGenerator.create(
               generator_type='TimeSeries',
               datasets=[dataset],
               generator_settings=settings,
            )
            g.id
            >>>'54e639a18bd88f08078ca831'
            g.generator_type
            >>>'TimeSeries'
        """
        data = {
            "generator_type": generator_type,
            "datasets": [d.to_dict() for d in datasets],
            "generator_settings": generator_settings.to_dict(),
        }
        response = cls._client.post(cls._path, data=data)
        finished_url = wait_for_async_resolution(cls._client, response.headers["Location"])
        finished_response = cls._client.get(finished_url)

        return cls.from_server_data(finished_response.json())

    @classmethod
    def get(cls, generator_id):
        """Gets information about a query generator.

        Parameters
        ----------
        generator_id : str
            The identifier of the query generator you want to load.

        Returns
        -------
        query_generator : DataEngineQueryGenerator
            The queried generator

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            g = dr.DataEngineQueryGenerator.get(generator_id='54e639a18bd88f08078ca831')
            g.id
            >>>'54e639a18bd88f08078ca831'
            g.generator_type
            >>>'TimeSeries'
        """
        path = f"{cls._path}{generator_id}/"
        return cls.from_location(path)

    def create_dataset(self, dataset_id=None, dataset_version_id=None, max_wait=DEFAULT_MAX_WAIT):
        """
        A blocking call that creates a new Dataset from the query generator.
        Returns when the dataset has been successfully processed. If optional
        parameters are not specified the query is applied to the dataset_id
        and dataset_version_id stored in the query generator. If specified they
        will override the stored dataset_id/dataset_version_id, i.e. to prep a
        prediction dataset.

        Parameters
        ----------
        dataset_id: Optional[str]
            The id of the unprepped dataset to apply the query to
        dataset_version_id: Optional[str]
            The version_id of the unprepped dataset to apply the query to

        Returns
        -------
        response: Dataset
            The Dataset created from the query generator
        """
        return Dataset.create_from_query_generator(
            self.id, dataset_id, dataset_version_id, max_wait
        )

    def prepare_prediction_dataset_from_catalog(
        self,
        project_id: str,
        dataset_id: str,
        dataset_version_id: Optional[str] = None,
        max_wait: Optional[int] = DEFAULT_MAX_WAIT,
        relax_known_in_advance_features_check: Optional[bool] = None,
    ) -> PredictionDataset:
        """Apply time series data prep to a catalog dataset and upload it to the project
        as a PredictionDataset.

        .. versionadded:: v3.1

        Parameters
        ----------
        project_id : str
            The id of the project to which you upload the prediction dataset.
        dataset_id : str
            The identifier of the dataset.
        dataset_version_id : Optional[str]
            The version id of the dataset to use.
        max_wait : Optional[int]
            Optional, the maximum number of seconds to wait before giving up.
        relax_known_in_advance_features_check : Optional[bool]
            For time series projects only. If True, missing values in the
            known in advance features are allowed in the forecast window at the prediction time.
            If omitted or False, missing values are not allowed.

        Returns
        -------
        dataset : PredictionDataset
            The newly uploaded dataset.
        """
        prediction_dataset = self.create_dataset(dataset_id, dataset_version_id, max_wait)
        project = Project.get(project_id)

        return project.upload_dataset_from_catalog(
            dataset_id=prediction_dataset.id,
            dataset_version_id=prediction_dataset.version_id,
            max_wait=max_wait,
            relax_known_in_advance_features_check=relax_known_in_advance_features_check,
        )

    def prepare_prediction_dataset(
        self,
        sourcedata: Union[str, pd.DataFrame, IOBase],
        project_id: str,
        max_wait: Optional[int] = DEFAULT_MAX_WAIT,
        relax_known_in_advance_features_check: Optional[bool] = None,
    ) -> PredictionDataset:
        """Apply time series data prep and upload the PredictionDataset to the project.

        .. versionadded:: v3.1

        Parameters
        ----------
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions. If it is a string, it can be either a path to a local file,
            or raw file content. If using a file on disk, the filename must consist of ASCII
            characters only.
        project_id : str
            The id of the project to which you upload the prediction dataset.
        max_wait : Optional[int]
            The maximum number of seconds to wait for the uploaded dataset to be processed before
            raising an error.
        relax_known_in_advance_features_check : Optional[bool]
            For time series projects only. If True, missing values in the
            known in advance features are allowed in the forecast window at the prediction time.
            If omitted or False, missing values are not allowed.
        Returns
        -------
        dataset : PredictionDataset
            The newly uploaded dataset.

        Raises
        ------
        InputNotUnderstoodError
            Raised if ``sourcedata`` isn't one of supported types.
        AsyncFailureError
            Raised if polling for the status of an async process resulted in a response with an
            unsupported status code.
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful (i.e. the server reported an error in
            uploading the dataset).
        AsyncTimeoutError
            Raised if processing the uploaded dataset took more time than specified
            by the ``max_wait`` parameter.
        """
        source_type = parse_source_type(sourcedata)
        if source_type not in (
            FileLocationType.PATH,
            LocalSourceType.DATA_FRAME,
            LocalSourceType.FILELIKE,
        ):
            raise InvalidUsageError(
                f"Unable to parse source ({sourcedata}) as filepath, DataFrame, or file."
            )

        dataset = Dataset.upload(sourcedata)
        prediction_dataset = self.create_dataset(dataset.id, dataset.version_id, max_wait)
        project = Project.get(project_id)
        return project.upload_dataset_from_catalog(
            dataset_id=prediction_dataset.id,
            dataset_version_id=prediction_dataset.version_id,
            max_wait=max_wait,
            relax_known_in_advance_features_check=relax_known_in_advance_features_check,
        )


class QueryGeneratorSettings:
    """
    A QueryGenerator settings to be used to create DataEngineQueryGenerator entity.
    .. versionadded:: v2.27
    Attributes
    ----------
    datetime_partition_column : str
        The date column that will be used as a datetime partition column
        in time series project.
    time_unit : str
        Indicates which unit is a basis for time steps of the output dataset.
    time_step : int
        Number of time steps for the output dataset.
    default_numeric_aggregation_method : str
        Default aggregation method used for numeric feature.
    default_categorical_aggregation_method : str
        Default aggregation method used for categorical feature.
    target : Optional[str]
        The name of target for the output dataset.
    multiseries_id_columns : list[str], optional
        An array with the names of columns identifying the series to which
        row of the output dataset belongs. Currently, only one multiseries
        ID column is supported.
    default_text_aggregation_method : Optional[str]
        Default aggregation method used for text feature.
    start_from_series_min_datetime : Optional[bool]
        A boolean value indicating whether post-aggregated series starts from series minimum
        datetime or global minimum datetime.
    end_to_series_max_datetime : Optional[bool]
        A boolean value indicating whether generates post-aggregated series up to series
        maximum datetime or global maximum datetime.
    Examples
    --------
    .. code-block:: python
        from datarobot.models.data_engine_query_generator import QueryGeneratorSettings
        query_generator_settings = QueryGeneratorSettings(
            datetime_partition_column='date',
            time_unit='DAY',
            time_step=1,
            default_numeric_aggregation_method='sum',
            default_categorical_aggregation_method='mostFrequent',
        )
    """

    def __init__(
        self,
        datetime_partition_column,
        time_unit,
        time_step,
        default_numeric_aggregation_method,
        default_categorical_aggregation_method,
        target=None,
        multiseries_id_columns=None,
        default_text_aggregation_method=None,
        start_from_series_min_datetime=True,
        end_to_series_max_datetime=True,
    ):
        self.datetime_partition_column = datetime_partition_column
        self.time_unit = time_unit
        self.time_step = time_step
        self.default_numeric_aggregation_method = default_numeric_aggregation_method
        self.default_categorical_aggregation_method = default_categorical_aggregation_method
        self.target = target
        self.multiseries_id_columns = multiseries_id_columns
        self.default_text_aggregation_method = default_text_aggregation_method
        self.start_from_series_min_datetime = start_from_series_min_datetime
        self.end_to_series_max_datetime = end_to_series_max_datetime

    def to_dict(self):
        return {
            "datetime_partition_column": self.datetime_partition_column,
            "time_unit": self.time_unit,
            "time_step": self.time_step,
            "default_numeric_aggregation_method": self.default_numeric_aggregation_method,
            "default_categorical_aggregation_method": self.default_categorical_aggregation_method,
            "target": self.target,
            "multiseries_id_columns": self.multiseries_id_columns,
            "default_text_aggregation_method": self.default_text_aggregation_method,
            "start_from_series_min_datetime": self.start_from_series_min_datetime,
            "end_to_series_max_datetime": self.end_to_series_max_datetime,
        }

    def to_payload(self):
        return {
            "datetimePartitionColumn": self.datetime_partition_column,
            "timeUnit": self.time_unit,
            "timeStep": self.time_step,
            "defaultNumericAggregationMethod": self.default_numeric_aggregation_method,
            "defaultCategoricalAggregationMethod": self.default_categorical_aggregation_method,
            "target": self.target,
            "multiseriesIdColumns": self.multiseries_id_columns,
            "defaultTextAggregationMethod": self.default_text_aggregation_method,
            "startFromSeriesMinDatetime": self.start_from_series_min_datetime,
            "endToSeriesMaxDatetime": self.end_to_series_max_datetime,
        }


class QueryGeneratorDataset:
    """
    A QueryGenerator dataset to be used to create DataEngineQueryGenerator entity.
    .. versionadded:: v2.27
    Attributes
    ----------
    alias : str
        The name for the dataset.
    dataset_id : str
        The identifier of the dataset.
    dataset_version_id : Optional[str]
        The version id of the dataset to use.
    Examples
    --------
    .. code-block:: python
        from datarobot.models.data_engine_query_generator import QueryGeneratorDataset
        query_generator_dataset = QueryGeneratorDataset(
            alias='My_Awesome_Dataset_csv',
            dataset_id='61093144cabd630828bca321',
            dataset_version_id=1,
        )
    """

    def __init__(self, alias, dataset_id, dataset_version_id=None):
        self.alias = alias
        self.dataset_id = dataset_id
        self.dataset_version_id = dataset_version_id

    def to_dict(self):
        return {
            "alias": self.alias,
            "dataset_id": self.dataset_id,
            "dataset_version_id": self.dataset_version_id,
        }

    def to_payload(self):
        return {
            "alias": self.alias,
            "datasetId": self.dataset_id,
            "datasetVersionId": self.dataset_version_id,
        }
