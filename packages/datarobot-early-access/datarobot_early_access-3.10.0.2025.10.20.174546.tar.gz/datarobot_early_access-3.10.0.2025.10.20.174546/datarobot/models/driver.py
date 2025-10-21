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

import os
from typing import Any, Dict, List, Optional

import trafaret as t

from datarobot._compat import String
from datarobot.enums import DataDriverListTypes, DataDriverTypes
from datarobot.models.api_object import APIObject


class DataDriver(APIObject):
    """A data driver

    Attributes
    ----------
    id : str
        the id of the driver.
    class_name : str
        the Java class name for the driver.
    canonical_name : str
        the user-friendly name of the driver.
    creator : str
        the id of the user who created the driver.
    base_names : List[str]
        a list of the file name(s) of the jar files.
    """

    _path = "externalDataDrivers/"
    _file_upload_path = "externalDataDriverFile/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("class_name", optional=True): t.Or(String, t.Null),
            t.Key("canonical_name"): String(),
            t.Key("creator"): String(),
            t.Key("base_names", optional=True): t.List(String()),
            t.Key("database_driver", optional=True): t.Or(String, t.Null),
            t.Key("type", default="jdbc", optional=True): String(),
            t.Key("version", optional=True): t.Or(String, t.Null),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id: Optional[str] = None,
        creator: Optional[str] = None,
        base_names: Optional[List[str]] = None,
        class_name: Optional[str] = None,
        canonical_name: Optional[str] = None,
        database_driver: Optional[str] = None,
        type: Optional[str] = None,
        version: Optional[str] = None,
    ) -> None:
        self._id = id
        self._creator = creator
        self._base_names = base_names
        self.class_name = class_name
        self.canonical_name = canonical_name
        self.database_driver = database_driver
        self.type = type
        self.version = version

    @classmethod
    def list(cls, typ: Optional[DataDriverListTypes] = None) -> List[DataDriver]:
        """
        Returns list of available drivers.

        Parameters
        ----------
        typ : DataDriverListTypes
            If specified, filters by specified driver type.

        Returns
        -------
        drivers : list of DataDriver instances
            contains a list of available drivers.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> drivers = dr.DataDriver.list()
            >>> drivers
            [DataDriver('mysql'), DataDriver('RedShift'), DataDriver('PostgreSQL')]
        """
        if typ is not None:
            r_data = cls._client.get(cls._path, params={"type": str(typ)}).json()
        else:
            r_data = cls._client.get(cls._path).json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    @classmethod
    def get(cls, driver_id: str) -> DataDriver:
        """
        Gets the driver.

        Parameters
        ----------
        driver_id : str
            the identifier of the driver.

        Returns
        -------
        driver : DataDriver
            the required driver.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.get('5ad08a1889453d0001ea7c5c')
            >>> driver
            DataDriver('PostgreSQL')
        """
        return cls.from_location(f"{cls._path}{driver_id}/")

    @classmethod
    def create(
        cls,
        class_name: str,
        canonical_name: str,
        files: Optional[List[str]] = None,
        typ: Optional[DataDriverTypes] = None,
        database_driver: Optional[str] = None,
    ) -> DataDriver:
        """
        Creates the driver. Only available to admin users.

        Parameters
        ----------
        class_name : str
            the Java class name for the driver. Specify None if typ is DataDriverTypes.DR_DATABASE_V1`.
        canonical_name : str
            the user-friendly name of the driver.
        files : List[str]
            a list of the file paths on file system file_path(s) for the driver.
        typ: str
            Optional. Specify the type of the driver. Defaults to `DataDriverTypes.JDBC`, may also be
            `DataDriverTypes.DR_DATABASE_V1`.
        database_driver: str
            Optional. Specify when typ is `DataDriverTypes.DR_DATABASE_V1` to create a native database
            driver. See `DrDatabaseV1Types` enum for some of the types, but that list may not be exhaustive.

        Returns
        -------
        driver : DataDriver
            the created driver.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.create(
            ...     class_name='org.postgresql.Driver',
            ...     canonical_name='PostgreSQL',
            ...     files=['/tmp/postgresql-42.2.2.jar']
            ... )
            >>> driver
            DataDriver('PostgreSQL')
        """
        payload: Dict[str, Any] = {}
        if typ and typ == DataDriverTypes.DR_DATABASE_V1:
            payload = {
                "type": str(typ),
                "databaseDriver": database_driver,
            }
        else:
            base_names: List[str] = []
            local_jar_urls: List[str] = []

            if files is not None:
                for file_path in files:
                    name = file_path.split(os.sep)[-1]
                    resp = cls._client.build_request_with_file(
                        "POST", cls._file_upload_path, name, file_path=file_path
                    ).json()
                    base_names.append(name)
                    local_jar_urls.append(resp["localUrl"])
            payload = {
                "className": class_name,
                "canonicalName": canonical_name,
                "localJarUrls": local_jar_urls,
                "baseNames": base_names,
            }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(
        self, class_name: Optional[str] = None, canonical_name: Optional[str] = None
    ) -> None:
        """
        Updates the driver. Only available to admin users.

        Parameters
        ----------
        class_name : str
            the Java class name for the driver.
        canonical_name : str
            the user-friendly name of the driver.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> driver = dr.DataDriver.get('5ad08a1889453d0001ea7c5c')
            >>> driver.canonical_name
            'PostgreSQL'
            >>> driver.update(canonical_name='postgres')
            >>> driver.canonical_name
            'postgres'
        """
        payload = {
            "className": class_name or self.class_name,
            "canonicalName": canonical_name or self.canonical_name,
        }
        r_data = self._client.patch(f"{self._path}{self.id}/", data=payload).json()
        self.class_name = r_data["className"]
        self.canonical_name = r_data["canonicalName"]

    def delete(self) -> None:
        """
        Removes the driver. Only available to admin users.

        Raises
        ------
        ClientError
            raised if user is not granted for `Can manage JDBC database drivers` feature
        """
        self._client.delete(f"{self._path}{self.id}/")

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def creator(self) -> Optional[str]:
        return self._creator

    @property
    def base_names(self) -> Optional[List[str]]:
        return self._base_names

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.canonical_name or self.id}')"
