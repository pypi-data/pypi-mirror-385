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
from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, cast

import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import from_api, parse_time, to_api

TFeaturelist = TypeVar("TFeaturelist", bound="Featurelist")
TModelingFeaturelist = TypeVar("TModelingFeaturelist", bound="ModelingFeaturelist")
TDatasetFeaturelist = TypeVar("TDatasetFeaturelist", bound="DatasetFeaturelist")

if TYPE_CHECKING:
    from datarobot._compat import TypedDict
    from datarobot.models.api_object import ServerDataDictType
    from datarobot.models.project import Project

    class DeleteFeatureListResult(TypedDict):
        dry_run: bool
        can_delete: bool
        deletion_blocked_reason: str
        num_affected_models: int
        num_affected_jobs: int


class BaseFeaturelist(APIObject):  # pylint: disable=missing-class-docstring
    _base_path: str  # path, to be overridden in inheriting classes
    # nulls are to account for the partial featurelist created inside models
    _converter = t.Dict(
        {
            t.Key("id"): t.Or(String, t.Null),
            t.Key("name"): t.Or(String, t.Null),
            t.Key("features"): t.Or(t.List(String), t.Null),
            t.Key("project_id"): t.Or(String(), t.Null),
            t.Key("created"): t.Or(t.Null, t.Call(parse_time)),
            t.Key("is_user_created"): t.Or(t.Bool, t.Null),
            t.Key("num_models"): t.Or(Int, t.Null),
            t.Key("description"): String(allow_blank=True),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        features: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        created: Optional[datetime] = None,
        is_user_created: Optional[bool] = None,
        num_models: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        self.id = id
        self.project_id = project_id
        self.name = name
        self.features = features
        self.created = created
        self.is_user_created = is_user_created
        self.num_models = num_models
        self.description = description

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def _make_url(self) -> str:
        return f"{self._base_path.format(self.project_id)}{self.id}/"

    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Update the name or description of an existing featurelist

        Note that only user-created featurelists can be renamed, and that names must not
        conflict with names used by other featurelists.

        Parameters
        ----------
        name : Optional[str]
            the new name for the featurelist
        description : Optional[str]
            the new description for the featurelist
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        self._client.patch(self._make_url(), data=data)
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description

    def delete(
        self, dry_run: bool = False, delete_dependencies: bool = False
    ) -> DeleteFeatureListResult:
        """Delete a featurelist, and any models and jobs using it

        All models using a featurelist, whether as the training featurelist or as a monotonic
        constraint featurelist, will also be deleted when the deletion is executed and any queued or
        running jobs using it will be cancelled. Similarly, predictions made on these models will
        also be deleted. All the entities that are to be deleted with a featurelist are described
        as "dependencies" of it.  To preview the results of deleting a featurelist, call delete
        with `dry_run=True`

        When deleting a featurelist with dependencies, users must specify `delete_dependencies=True`
        to confirm they want to delete the featurelist and all its dependencies. Without that
        option, only featurelists with no dependencies may be successfully deleted and others will
        error.

        Featurelists configured into the project as a default featurelist or as a default monotonic
        constraint featurelist cannot be deleted.

        Featurelists used in a model deployment cannot be deleted until the model deployment is
        deleted.

        Parameters
        ----------
        dry_run : Optional[bool]
            specify True to preview the result of deleting the featurelist, instead of actually
            deleting it.
        delete_dependencies : Optional[bool]
            specify True to successfully delete featurelists with dependencies; if left
            False by default, featurelists without dependencies can be successfully deleted and
            those with dependencies will error upon attempting to delete them.

        Returns
        -------
        result : dict
            A dictionary describing the result of deleting the featurelist, with the following keys
                - dry_run : bool, whether the deletion was a dry run or an actual deletion
                - can_delete : bool, whether the featurelist can actually be deleted
                - deletion_blocked_reason : str, why the featurelist can't be deleted (if it can't)
                - num_affected_models : int, the number of models using this featurelist
                - num_affected_jobs : int, the number of jobs using this featurelist
        """
        result = self._client.delete(
            self._make_url(),
            params=to_api({"dry_run": dry_run, "delete_dependencies": delete_dependencies}),
        )
        checker = t.Dict(
            {
                t.Key("dry_run"): t.Bool(),
                t.Key("can_delete"): t.Bool(),
                t.Key("deletion_blocked_reason"): String(allow_blank=True),
                t.Key("num_affected_models"): Int(),
                t.Key("num_affected_jobs"): Int(),
            }
        ).ignore_extra("*")
        return cast("DeleteFeatureListResult", checker.check(from_api(result.json())))


class Featurelist(BaseFeaturelist):
    """A set of features used in modeling

    Attributes
    ----------
    id : str
        the id of the featurelist
    name : str
        the name of the featurelist
    features : List[str]
        the names of all the Features in the featurelist
    project_id : str
        the project the featurelist belongs to
    created : datetime.datetime
        (New in version v2.13) when the featurelist was created
    is_user_created : bool
        (New in version v2.13) whether the featurelist was created by a user or by DataRobot
        automation
    num_models : int
        (New in version v2.13) the number of models currently using this featurelist.  A model is
        considered to use a featurelist if it is used to train the model or as a monotonic
        constraint featurelist, or if the model is a blender with at least one component model
        using the featurelist.
    description : str
        (New in version v2.13) the description of the featurelist.  Can be updated by the user
        and may be supplied by default for DataRobot-created featurelists.
    """

    _base_path = "projects/{}/featurelists/"
    _project: Project

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        features: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        created: Optional[datetime] = None,
        is_user_created: Optional[bool] = None,
        num_models: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            features=features,
            project_id=project_id,
            created=created,
            is_user_created=is_user_created,
            num_models=num_models,
            description=description,
        )
        self._set_up(self.project_id)

    @property
    def project(self) -> Project:
        return self._project

    def _set_up(self, project_id: Optional[str]) -> None:
        from datarobot.models.project import (  # pylint: disable=import-outside-toplevel,cyclic-import
            Project,
        )

        self._project = Project(project_id)

    @classmethod
    def from_data(cls: Type[TFeaturelist], data: ServerDataDictType) -> TFeaturelist:  # type: ignore[override]
        """Overrides the parent method to ensure description is always populated

        Parameters
        ----------
        data : dict
            the data from the server, having gone through processing
        """
        # these keys are sometimes missing b/c dummy featurelists are instantiated inside models
        # in _normal_ usage these should all be supplied
        for key in [
            "features",
            "num_models",
            "is_user_created",
            "created",
            "id",
            "name",
            "project_id",
        ]:
            data.setdefault(key, None)
        if "description" not in data:
            data["description"] = ""
        return super().from_data(data)

    @classmethod
    def get(cls: Type[TFeaturelist], project_id: str, featurelist_id: str) -> TFeaturelist:
        """Retrieve a known feature list

        Parameters
        ----------
        project_id : str
            The id of the project the featurelist is associated with
        featurelist_id : str
            The ID of the featurelist to retrieve

        Returns
        -------
        featurelist : Featurelist
            The queried instance

        Raises
        ------
        ValueError
            passed ``project_id`` parameter value is of not supported type
        """
        from datarobot.models.project import (  # pylint: disable=import-outside-toplevel,cyclic-import
            Project,
        )

        if isinstance(project_id, Project):  # type: ignore[unreachable]
            project_id = project_id.id  # type: ignore[unreachable]
        elif isinstance(project_id, str):
            pass
        else:
            raise ValueError("Project arg must be Project instance or str")

        url = f"{cls._base_path.format(project_id)}{featurelist_id}/"
        return cls.from_location(url)


class ModelingFeaturelist(BaseFeaturelist):
    """A set of features that can be used to build a model

    In time series projects, a new set of modeling features is created after setting the
    partitioning options.  These features are automatically derived from those in the project's
    dataset and are the features used for modeling.  Modeling features are only accessible once
    the target and partitioning options have been set.  In projects that don't use time series
    modeling, once the target has been set, ModelingFeaturelists and Featurelists will behave
    the same.

    For more information about input and modeling features, see the
    :ref:`time series documentation<input-vs-modeling>`.

    Attributes
    ----------
    id : str
        the id of the modeling featurelist
    project_id : str
        the id of the project the modeling featurelist belongs to
    name : str
        the name of the modeling featurelist
    features : List[str]
        a list of the names of features included in this modeling featurelist
    created : datetime.datetime
        (New in version v2.13) when the featurelist was created
    is_user_created : bool
        (New in version v2.13) whether the featurelist was created by a user or by DataRobot
        automation
    num_models : int
        (New in version v2.13) the number of models currently using this featurelist.  A model is
        considered to use a featurelist if it is used to train the model or as a monotonic
        constraint featurelist, or if the model is a blender with at least one component model
        using the featurelist.
    description : str
        (New in version v2.13) the description of the featurelist.  Can be updated by the user
        and may be supplied by default for DataRobot-created featurelists.
    """

    _base_path = "projects/{}/modelingFeaturelists/"

    @classmethod
    def get(
        cls: Type[TModelingFeaturelist], project_id: str, featurelist_id: str
    ) -> TModelingFeaturelist:
        """Retrieve a modeling featurelist

        Modeling featurelists can only be retrieved once the target and partitioning options have
        been set.

        Parameters
        ----------
        project_id : str
            the id of the project the modeling featurelist belongs to
        featurelist_id : str
             the id of the modeling featurelist to retrieve

        Returns
        -------
        featurelist : ModelingFeaturelist
            the specified featurelist
        """
        url = f"{cls._base_path.format(project_id)}{featurelist_id}/"
        return cls.from_location(url)


class DatasetFeaturelist(APIObject):
    """A set of features attached to a dataset in the AI Catalog

    Attributes
    ----------
    id : str
        the id of the dataset featurelist
    dataset_id : str
        the id of the dataset the featurelist belongs to
    dataset_version_id: Optional[str]
        the version id of the dataset this featurelist belongs to
    name : str
        the name of the dataset featurelist
    features : List[str]
        a list of the names of features included in this dataset featurelist
    creation_date : datetime.datetime
        when the featurelist was created
    created_by : str
        the user name of the user who created this featurelist
    user_created : bool
        whether the featurelist was created by a user or by DataRobot automation
    description : Optional[str]
        the description of the featurelist. Only present on DataRobot-created featurelists.
    """

    _base_path = "datasets/{}/featurelists/"
    _converter = t.Dict(
        {
            t.Key("id"): t.Or(String, t.Null),
            t.Key("name"): t.Or(String, t.Null),
            t.Key("features"): t.Or(t.List(String), t.Null),
            t.Key("dataset_id"): t.Or(String, t.Null),
            t.Key("dataset_version_id", optional=True): t.Or(String, t.Null),
            t.Key("creation_date"): t.Or(t.Null, t.Call(parse_time)),
            t.Key("created_by"): t.Or(String, t.Null),
            t.Key("user_created"): t.Or(t.Bool, t.Null),
            t.Key("description", optional=True): String(allow_blank=True),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        features: Optional[List[str]] = None,
        dataset_id: Optional[str] = None,
        dataset_version_id: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        created_by: Optional[str] = None,
        user_created: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.features = features
        self.dataset_id = dataset_id
        self.dataset_version_id = dataset_version_id
        self.creation_date = creation_date
        self.created_by = created_by
        self.user_created = user_created
        self.description = description

    def _make_url(self) -> str:
        return f"{self._base_path.format(self.dataset_id)}{self.id}/"

    @classmethod
    def get(
        cls: Type[TDatasetFeaturelist], dataset_id: str, featurelist_id: str
    ) -> TDatasetFeaturelist:
        """Retrieve a dataset featurelist

        Parameters
        ----------
        dataset_id : str
            the id of the dataset the featurelist belongs to
        featurelist_id : str
             the id of the dataset featurelist to retrieve

        Returns
        -------
        featurelist : DatasetFeatureList
            the specified featurelist
        """
        url = f"{cls._base_path.format(dataset_id)}{featurelist_id}/"
        return cls.from_location(url)

    def delete(self) -> None:
        """Delete a dataset featurelist

        Featurelists configured into the dataset as a default featurelist cannot be deleted.
        """
        self._client.delete(self._make_url())

    def update(self, name: Optional[str] = None) -> None:
        """Update the name of an existing featurelist

        Note that only user-created featurelists can be renamed, and that names must not
        conflict with names used by other featurelists.

        Parameters
        ----------
        name : Optional[str]
            the new name for the featurelist
        """
        data = {}
        if name is not None:
            data["name"] = name
        self._client.patch(self._make_url(), data=data)
        if name is not None:
            self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
