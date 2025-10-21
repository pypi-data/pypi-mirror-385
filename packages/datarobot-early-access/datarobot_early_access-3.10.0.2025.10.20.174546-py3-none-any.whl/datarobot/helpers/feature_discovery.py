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

from ..enums import SNAPSHOT_POLICY

if TYPE_CHECKING:
    from datarobot._compat import TypedDict

    class SecondaryDatasetDict(TypedDict):
        identifier: str
        catalog_id: str
        catalog_version_id: str
        snapshot_policy: str


FeatureDerivationWindowsType = List[Dict[str, Union[int, str]]]
RelationshipDictType = Dict[
    str,
    Union[
        None,
        str,
        int,
        List[str],
        FeatureDerivationWindowsType,
    ],
]

__all__ = (
    "DatasetDefinition",
    "FeatureDiscoverySetting",
    "Relationship",
    "SecondaryDataset",
)


class DatasetDefinition:
    """Dataset definition for the Feature Discovery

    .. versionadded:: v2.25

    Attributes
    ----------
    identifier: str
        Alias of the dataset (used directly as part of the generated feature names)
    catalog_id: Optional[str]
        Identifier of the catalog item
    catalog_version_id: str
        Identifier of the catalog item version
    primary_temporal_key: Optional[str]
        Name of the column indicating time of record creation
    feature_list_id: Optional[str]
        Identifier of the feature list. This decides which columns in the dataset are
        used for feature generation
    snapshot_policy: Optional[str]
        Policy to use  when creating a project or making predictions.
        If omitted, by default endpoint will use 'latest'.
        Must be one of the following values:
        'specified': Use specific snapshot specified by catalogVersionId
        'latest': Use latest snapshot from the same catalog item
        'dynamic': Get data from the source (only applicable for JDBC datasets)

    Examples
    --------
    .. code-block:: python

        import datarobot as dr
        dataset_definition = dr.DatasetDefinition(
            identifier='profile',
            catalog_id='5ec4aec1f072bc028e3471ae',
            catalog_version_id='5ec4aec2f072bc028e3471b1',
        )

        dataset_definition = dr.DatasetDefinition(
            identifier='transaction',
            catalog_id='5ec4aec1f072bc028e3471ae',
            catalog_version_id='5ec4aec2f072bc028e3471b1',
            primary_temporal_key='Date'
        )
    """

    def __init__(
        self,
        identifier: str,
        catalog_id: Optional[str],
        catalog_version_id: str,
        snapshot_policy: str = SNAPSHOT_POLICY.LATEST,
        feature_list_id: Optional[str] = None,
        primary_temporal_key: Optional[str] = None,
    ):
        self.identifier = identifier
        self.catalog_id = catalog_id
        self.catalog_version_id = catalog_version_id
        self.snapshot_policy = snapshot_policy
        self.primary_temporal_key = primary_temporal_key
        self.feature_list_id = feature_list_id

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "identifier": self.identifier,
            "catalog_id": self.catalog_id,
            "catalog_version_id": self.catalog_version_id,
            "snapshot_policy": self.snapshot_policy,
            "primary_temporal_key": self.primary_temporal_key,
            "feature_list_id": self.feature_list_id,
        }

    # pylint: disable-next=missing-function-docstring
    def to_payload(self) -> Dict[str, Optional[str]]:
        payload = {
            "identifier": self.identifier,
            "catalogId": self.catalog_id,
            "catalogVersionId": self.catalog_version_id,
            "snapshotPolicy": self.snapshot_policy,
        }
        if self.primary_temporal_key:
            payload["primaryTemporalKey"] = self.primary_temporal_key
        if self.feature_list_id:
            payload["featureListId"] = self.feature_list_id
        return payload


class Relationship:
    """Relationship between dataset defined in DatasetDefinition

    .. versionadded:: v2.25

    Attributes
    ----------
    dataset1_identifier: Optional[str]
        Identifier of the first dataset in this relationship.
        This is specified in the identifier field of dataset_definition structure.
        If None, then the relationship is with the primary dataset.
    dataset2_identifier: str
        Identifier of the second dataset in this relationship.
        This is specified in the identifier field of dataset_definition schema.
    dataset1_keys: List[str]
        (max length: 10 min length: 1)
        Column(s) from the first dataset which are used to join to the second dataset
    dataset2_keys: List[str]
        (max length: 10 min length: 1)
        Column(s) from the second dataset that are used to join to the first dataset
    feature_derivation_window_start: int, or None
        How many time_units of each dataset's primary temporal key into the past relative
        to the datetimePartitionColumn the feature derivation window should begin.
        Will be a negative integer,
        If present, the feature engineering Graph will perform time-aware joins.
    feature_derivation_window_end: Optional[int]
        How many timeUnits of each dataset's record
        primary temporal key into the past relative to the datetimePartitionColumn the
        feature derivation window should end.  Will be a non-positive integer, if present.
        If present, the feature engineering Graph will perform time-aware joins.
    feature_derivation_window_time_unit: Optional[int]
        Time unit of the feature derivation window.
        One of ``datarobot.enums.AllowedTimeUnitsSAFER``
        If present, time-aware joins will be used.
        Only applicable when dataset1_identifier is not provided.
    feature_derivation_windows: list of dict, or None
        List of feature derivation windows settings. If present, time-aware joins will be used.
        Only allowed when feature_derivation_window_start,
        feature_derivation_window_end and feature_derivation_window_time_unit are not provided.
    prediction_point_rounding: Optional[int]
        Closest value of prediction_point_rounding_time_unit to round the prediction point
        into the past when applying the feature derivation window. Will be a positive integer,
        if present.Only applicable when dataset1_identifier is not provided.
    prediction_point_rounding_time_unit: Optional[str]
        Time unit of the prediction point rounding.
        One of ``datarobot.enums.AllowedTimeUnitsSAFER``
        Only applicable when dataset1_identifier is not provided.

    The `feature_derivation_windows` is a list of dictionary with schema:
        start: int
            How many time_units of each dataset's primary temporal key into the past relative
            to the datetimePartitionColumn the feature derivation window should begin.
        end: int
            How many timeUnits of each dataset's record
            primary temporal key into the past relative to the datetimePartitionColumn the
            feature derivation window should end.
        unit: str
            Time unit of the feature derivation window.
            One of ``datarobot.enums.AllowedTimeUnitsSAFER``.

    Examples
    --------
    .. code-block:: python

        import datarobot as dr
        relationship = dr.Relationship(
            dataset1_identifier='profile',
            dataset2_identifier='transaction',
            dataset1_keys=['CustomerID'],
            dataset2_keys=['CustomerID']
        )

        relationship = dr.Relationship(
            dataset2_identifier='profile',
            dataset1_keys=['CustomerID'],
            dataset2_keys=['CustomerID'],
            feature_derivation_window_start=-14,
            feature_derivation_window_end=-1,
            feature_derivation_window_time_unit='DAY',
            prediction_point_rounding=1,
            prediction_point_rounding_time_unit='DAY'
        )
    """

    def __init__(
        self,
        dataset2_identifier: str,
        dataset1_keys: List[str],
        dataset2_keys: List[str],
        dataset1_identifier: Optional[str] = None,
        feature_derivation_window_start: Optional[int] = None,
        feature_derivation_window_end: Optional[int] = None,
        feature_derivation_window_time_unit: Optional[int] = None,
        feature_derivation_windows: Optional[FeatureDerivationWindowsType] = None,
        prediction_point_rounding: Optional[int] = None,
        prediction_point_rounding_time_unit: Optional[str] = None,
    ) -> None:
        self.dataset1_identifier = dataset1_identifier
        self.dataset2_identifier = dataset2_identifier
        self.dataset1_keys = dataset1_keys
        self.dataset2_keys = dataset2_keys
        self.feature_derivation_window_start = feature_derivation_window_start
        self.feature_derivation_window_end = feature_derivation_window_end
        self.feature_derivation_window_time_unit = feature_derivation_window_time_unit
        self.feature_derivation_windows = feature_derivation_windows
        self.prediction_point_rounding = prediction_point_rounding
        self.prediction_point_rounding_time_unit = prediction_point_rounding_time_unit

    def to_dict(self) -> RelationshipDictType:
        return {
            "dataset1_identifier": self.dataset1_identifier,
            "dataset2_identifier": self.dataset2_identifier,
            "dataset1_keys": self.dataset1_keys,
            "dataset2_keys": self.dataset2_keys,
            "feature_derivation_window_start": self.feature_derivation_window_start,
            "feature_derivation_window_end": self.feature_derivation_window_end,
            "feature_derivation_window_time_unit": self.feature_derivation_window_time_unit,
            "feature_derivation_windows": self.feature_derivation_windows,
            "prediction_point_rounding": self.prediction_point_rounding,
            "prediction_point_rounding_time_unit": self.prediction_point_rounding_time_unit,
        }

    def to_payload(self) -> RelationshipDictType:  # pylint: disable=missing-function-docstring
        payload: RelationshipDictType = {
            "dataset2Identifier": self.dataset2_identifier,
            "dataset1Keys": self.dataset1_keys,
            "dataset2Keys": self.dataset2_keys,
        }
        if self.dataset1_identifier:
            payload["dataset1Identifier"] = self.dataset1_identifier
        if self.feature_derivation_window_start is not None:
            payload["featureDerivationWindowStart"] = self.feature_derivation_window_start
        if self.feature_derivation_window_end is not None:
            payload["featureDerivationWindowEnd"] = self.feature_derivation_window_end
        if self.feature_derivation_window_time_unit:
            payload["featureDerivationWindowTimeUnit"] = self.feature_derivation_window_time_unit
        if self.feature_derivation_windows is not None:
            payload["featureDerivationWindows"] = self.feature_derivation_windows
        if self.prediction_point_rounding is not None:
            payload["predictionPointRounding"] = self.prediction_point_rounding
        if self.prediction_point_rounding_time_unit:
            payload["predictionPointRoundingTimeUnit"] = self.prediction_point_rounding_time_unit
        return payload


class SecondaryDataset:
    """A secondary dataset to be used for feature discovery

    .. versionadded:: v2.25

    Attributes
    ----------
    identifier: str
        Alias of the dataset (used directly as part of the generated feature names)
    catalog_id: str
        Identifier of the catalog item
    catalog_version_id: str
        Identifier of the catalog item version
    snapshot_policy: Optional[str]
        Policy to use while creating a project or making predictions.
        If omitted, by default endpoint will use 'latest'.
        Must be one of the following values:
        'specified': Use specific snapshot specified by catalogVersionId
        'latest': Use latest snapshot from the same catalog item
        'dynamic': Get data from the source (only applicable for JDBC datasets)

    Examples
    --------
    .. code-block:: python

        import datarobot as dr
        dataset_definition = dr.SecondaryDataset(
            identifier='profile',
            catalog_id='5ec4aec1f072bc028e3471ae',
            catalog_version_id='5ec4aec2f072bc028e3471b1',
        )
    """

    def __init__(
        self,
        identifier: str,
        catalog_id: str,
        catalog_version_id: str,
        snapshot_policy: str = SNAPSHOT_POLICY.LATEST,
    ) -> None:
        self.identifier = identifier
        self.catalog_id = catalog_id
        self.catalog_version_id = catalog_version_id
        self.snapshot_policy = snapshot_policy

    def to_dict(self) -> SecondaryDatasetDict:
        return {
            "identifier": self.identifier,
            "catalog_id": self.catalog_id,
            "catalog_version_id": self.catalog_version_id,
            "snapshot_policy": self.snapshot_policy,
        }

    def to_payload(self) -> Dict[str, Optional[str]]:
        return {
            "identifier": self.identifier,
            "catalogId": self.catalog_id,
            "catalogVersionId": self.catalog_version_id,
            "snapshotPolicy": self.snapshot_policy,
        }


class FeatureDiscoverySetting:
    """A feature discovery settings used to customize the feature discovery process

    To see the list of possible settings, create a RelationshipConfiguration without specifying
    settings and check its `feature_discovery_settings` attribute, which is a list of possible
    settings with their default values.

    Attributes
    ----------
    name: str
        Name of the feature discovery setting
    value: bool
        Value of the feature discovery setting

    .. versionadded: v2.26
    """

    def __init__(self, name: str, value: bool) -> None:
        self.name = name
        self.value = value

    def to_dict(self) -> Dict[str, Union[str, bool]]:
        return {
            "name": self.name,
            "value": self.value,
        }
