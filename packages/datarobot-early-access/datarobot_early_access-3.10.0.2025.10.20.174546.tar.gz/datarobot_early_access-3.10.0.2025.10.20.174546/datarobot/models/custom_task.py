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

from typing import Iterable, List, Optional

import trafaret as t

from datarobot._compat import String
from datarobot.enums import CUSTOM_TASK_LANGUAGE, CUSTOM_TASK_TARGET_TYPE
from datarobot.models.api_object import APIObject, ServerDataType
from datarobot.models.custom_task_version import CustomTaskVersion
from datarobot.models.sharing import SharingAccess
from datarobot.utils.pagination import unpaginate


class CustomTask(APIObject):
    """A custom task. This can be in a partial state or a complete state.
    When the `latest_version` is `None`, the empty task has been initialized with
    some metadata.  It is not yet use-able for actual training.  Once the first
    `CustomTaskVersion` has been created, you can put the CustomTask in UserBlueprints to
    train Models in Projects

    .. versionadded:: v2.26

    Attributes
    ----------
    id: str
        id of the custom task
    name: str
        name of the custom task
    language: str
        programming language of the custom task.
        Can be "python", "r", "java" or "other"
    description: str
        description of the custom task
    target_type: datarobot.enums.CUSTOM_TASK_TARGET_TYPE
        the target type of the custom task. One of:

        - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.BINARY`
        - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.REGRESSION`
        - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.MULTICLASS`
        - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.ANOMALY`
        - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.TRANSFORM`
    latest_version: datarobot.CustomTaskVersion or None
        latest version of the custom task if the task has a latest version. If the
        latest version is None, the custom task is not ready for use in user blueprints.
        You must create its first CustomTaskVersion before you can use the CustomTask
    created_by: str
        The username of the user who created the custom task.
    updated_at: str
        An ISO-8601 formatted timestamp of when the custom task was updated.
    created_at: str
        ISO-8601 formatted timestamp of when the custom task was created
    calibrate_predictions: bool
        whether anomaly predictions should be calibrated to be between 0 and 1 by DR.
        only applies to custom estimators with target type
        `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.ANOMALY`
    """

    _path = "customTasks/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("target_type"): String(),
            t.Key("latest_version", optional=True, default=None): CustomTaskVersion.schema
            | t.Null(),
            t.Key("created") >> "created_at": String(),
            t.Key("updated") >> "updated_at": String(),
            t.Key("name"): String(),
            t.Key("description"): String(allow_blank=True),
            t.Key("language"): String(allow_blank=True),
            t.Key("created_by"): String(),
            t.Key("calibrate_predictions", optional=True): t.Bool(),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(
        self,
        id: str,
        target_type: CUSTOM_TASK_TARGET_TYPE,
        latest_version: Optional[CustomTaskVersion],
        created_at: str,
        updated_at: str,
        name: str,
        description: str,
        language: CUSTOM_TASK_LANGUAGE,
        created_by: str,
        calibrate_predictions: Optional[bool] = None,
    ) -> None:
        if latest_version is not None:
            # TODO: Annotate CustomTaskVersion
            latest_version = CustomTaskVersion(**latest_version)  # type: ignore[no-untyped-call, arg-type]

        self.id = id
        self.target_type = target_type
        self.latest_version = latest_version
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.description = description
        self.language = language
        self.created_by = created_by
        self.calibrate_predictions = calibrate_predictions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name or self.id!r})"

    def _update_values(self, new_response: CustomTask) -> None:
        for attr in self._fields():
            new_value = getattr(new_response, attr)
            setattr(self, attr, new_value)

    @classmethod
    def from_server_data(
        cls, data: ServerDataType, keep_attrs: Optional[Iterable[str]] = None
    ) -> CustomTask:
        raw_task: CustomTask = super().from_server_data(data, keep_attrs)
        # from_server_data will make the keys in requiredMetadata lowercase,
        # which is not OK. we need to preserve case
        latest_version_data = data.get("latestVersion")  # type: ignore[union-attr]
        if latest_version_data is not None:
            raw_task.latest_version.required_metadata = latest_version_data.get(  # type: ignore[union-attr]
                "requiredMetadata"
            )
        return raw_task

    @classmethod
    def list(
        cls, order_by: Optional[str] = None, search_for: Optional[str] = None
    ) -> List[CustomTask]:
        """List custom tasks available to the user.

        .. versionadded:: v2.26

        Parameters
        ----------
        search_for: Optional[str]
            string for filtering custom tasks - only tasks that contain the
            string in name or description will be returned.
            If not specified, all custom task will be returned
        order_by: Optional[str]
            property to sort custom tasks by.
            Supported properties are "created" and "updated".
            Prefix the attribute name with a dash to sort in descending order,
            e.g. order_by='-created'.
            By default, the order_by parameter is None which will result in
            custom tasks being returned in order of creation time descending

        Returns
        -------
        List[CustomTask]
            a list of custom tasks.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        payload = {
            "order_by": order_by,
            "search_for": search_for,
        }
        data = unpaginate(cls._path, payload, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, custom_task_id: str) -> CustomTask:
        """Get custom task by id.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            id of the custom task

        Returns
        -------
        CustomTask
            retrieved custom task

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = f"{cls._path}{custom_task_id}/"
        data = cls._client.get(path).json()
        return cls.from_server_data(data)

    @classmethod
    def copy(cls, custom_task_id: str) -> CustomTask:
        """Create a custom task by copying existing one.

        .. versionadded:: v2.26

        Parameters
        ----------
        custom_task_id: str
            id of the custom task to copy

        Returns
        -------
        CustomTask

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        path = f"{cls._path}fromCustomTask/"
        response = cls._client.post(path, data={"custom_task_id": custom_task_id})
        return cls.from_server_data(response.json())

    @classmethod
    def create(  # type: ignore[no-untyped-def]
        cls,
        name: str,
        target_type: CUSTOM_TASK_TARGET_TYPE,
        language: Optional[CUSTOM_TASK_LANGUAGE] = None,
        description: Optional[str] = None,
        calibrate_predictions: Optional[bool] = None,
        **kwargs,
    ) -> CustomTask:
        """
        Creates *only the metadata* for a custom task.  This task will
        not be use-able until you have created a CustomTaskVersion attached to this task.

        .. versionadded:: v2.26

        Parameters
        ----------
        name: str
            name of the custom task
        target_type: datarobot.enums.CUSTOM_TASK_TARGET_TYPE
            the target typed based on the following values. Anything else will raise an error

            - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.BINARY`
            - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.REGRESSION`
            - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.MULTICLASS`
            - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.ANOMALY`
            - `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.TRANSFORM`
        language: Optional[str]
            programming language of the custom task.
            Can be "python", "r", "java" or "other"
        description: Optional[str]
            description of the custom task
        calibrate_predictions: Optional[bool]
            whether anomaly predictions should be calibrated to be between 0 and 1 by DR.
            if None, uses default value from DR app (True).
            only applies to custom estimators with target type
            `datarobot.enums.CUSTOM_TASK_TARGET_TYPE.ANOMALY`

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.

        Returns
        -------
        CustomTask
        """
        cls._validate_target_type(target_type)
        payload = {k: v for k, v in kwargs.items()}  # pylint: disable=unnecessary-comprehension
        payload.update({"name": name, "target_type": target_type})
        for k, v in [
            ("language", language),
            ("description", description),
            ("calibrate_predictions", calibrate_predictions),
        ]:
            if v is not None:
                payload[k] = v

        response = cls._client.post(cls._path, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    def _validate_target_type(cls, target_type: CUSTOM_TASK_TARGET_TYPE) -> None:
        if target_type not in CUSTOM_TASK_TARGET_TYPE.ALL:
            raise ValueError(f"{target_type} is not one of {CUSTOM_TASK_TARGET_TYPE.ALL}")

    def update(  # type: ignore[no-untyped-def]
        self,
        name: Optional[str] = None,
        language: Optional[CUSTOM_TASK_LANGUAGE] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Update custom task properties.

        .. versionadded:: v2.26

        Parameters
        ----------
        name: Optional[str]
            new custom task name
        language: Optional[str]
            new custom task programming language
        description: Optional[str]
            new custom task description

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        payload = {k: v for k, v in kwargs.items()}  # pylint: disable=unnecessary-comprehension
        for k, v in [("name", name), ("language", language), ("description", description)]:
            if v is not None:
                payload[k] = v

        url = f"{self._path}{self.id}/"
        data = self._client.patch(url, data=payload).json()
        new_obj = self.from_server_data(data)
        self._update_values(new_obj)

    def refresh(self) -> None:
        """Update custom task with the latest data from server.

        .. versionadded:: v2.26

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """

        new_object = self.get(self.id)
        self._update_values(new_object)

    def delete(self) -> None:
        """Delete custom task.

        .. versionadded:: v2.26

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = f"{self._path}{self.id}/"
        self._client.delete(url)

    def download_latest_version(self, file_path: str) -> None:
        """Download the latest custom task version.

        .. versionadded:: v2.26

        Parameters
        ----------
        file_path: str
            the full path of the target zip file

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        path = f"{self._path}{self.id}/download/"
        response = self._client.get(path)
        with open(file_path, "wb") as f:
            f.write(response.content)

    def get_access_list(self) -> List[SharingAccess]:
        """Retrieve access control settings of this custom task.

        .. versionadded:: v2.27

        Returns
        -------
        list of :class:`SharingAccess <datarobot.SharingAccess>`
        """
        url = f"{self._path}{self.id}/accessControl/"
        return [
            SharingAccess.from_server_data(datum) for datum in unpaginate(url, {}, self._client)
        ]

    def share(self, access_list: List[SharingAccess]) -> None:
        """Update the access control settings of this custom task.

        .. versionadded:: v2.27

        Parameters
        ----------
        access_list : list of :class:`SharingAccess <datarobot.SharingAccess>`
            A list of SharingAccess to update.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status

        Examples
        --------
        Transfer access to the custom task from old_user@datarobot.com to new_user@datarobot.com

        .. code-block:: python

            import datarobot as dr

            new_access = dr.SharingAccess(new_user@datarobot.com,
                                          dr.enums.SHARING_ROLE.OWNER, can_share=True)
            access_list = [dr.SharingAccess(old_user@datarobot.com, None), new_access]

            dr.CustomTask.get('custom-task-id').share(access_list)
        """
        payload = {
            "data": [access.collect_payload() for access in access_list],
        }
        nullable_query_params = {"role"}
        self._client.patch(
            f"{self._path}{self.id}/accessControl/",
            data=payload,
            keep_attrs=nullable_query_params,
        )
