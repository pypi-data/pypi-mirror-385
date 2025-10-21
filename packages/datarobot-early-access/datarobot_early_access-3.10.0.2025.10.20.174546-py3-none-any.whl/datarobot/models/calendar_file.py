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
import json
import os
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Union

from requests import Response
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.models.sharing import SharingAccess
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution

from .. import errors

if TYPE_CHECKING:
    from datarobot._compat import TypedDict

    class CountryCode(TypedDict):
        name: str
        code: str


class CalendarFile(APIObject):
    """Represents the data for a calendar file.

    For more information about calendar files, see the
    :ref:`calendar documentation <calendar-files>`.

    Attributes
    ----------
    id : str
        The id of the calendar file.
    calendar_start_date : str
        The earliest date in the calendar.
    calendar_end_date : str
        The last date in the calendar.
    created  : str
        The date this calendar was created, i.e. uploaded to DR.
    name : str
        The name of the calendar.
    num_event_types : int
        The number of different event types.
    num_events : int
        The number of events this calendar has.
    project_ids : list of strings
        A list containing the projectIds of the projects using this calendar.
    multiseries_id_columns: List[str] or None
        A list of columns in calendar which uniquely identify events for different series.
        Currently, only one column is supported.
        If multiseries id columns are not provided, calendar is considered to be single series.
    role : str
        The access role the user has for this calendar.
    """

    _base_url = "calendars/"

    _upload_url = _base_url + "fileUpload/"
    _calendar_url = _base_url + "{}/"
    _access_control_url = _calendar_url + "accessControl/"
    _from_country_code_url = _base_url + "fromCountryCode/"
    _from_dataset_url = _base_url + "fromDataset/"
    _allowed_countries_list_url = "calendarCountryCodes/"

    _converter = t.Dict(
        {
            t.Key("calendar_end_date"): String,
            t.Key("calendar_start_date"): String,
            t.Key("created"): String,
            t.Key("id"): String,
            t.Key("name"): String,
            t.Key("num_event_types"): Int,
            t.Key("num_events"): Int,
            t.Key("project_ids"): t.List(String),
            t.Key("role"): String,
            t.Key("multiseries_id_columns", optional=True): t.Or(t.List(String), t.Null),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        calendar_end_date: Optional[str] = None,
        calendar_start_date: Optional[str] = None,
        created: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        num_event_types: Optional[int] = None,
        num_events: Optional[int] = None,
        project_ids: Optional[List[str]] = None,
        role: Optional[str] = None,
        multiseries_id_columns: Optional[List[str]] = None,
    ) -> None:
        self.calendar_end_date = calendar_end_date
        self.calendar_start_date = calendar_start_date
        self.created = created
        self.id = id
        self.name = name
        self.num_event_types = num_event_types
        self.num_events = num_events
        self.project_ids = project_ids
        self.role = role
        self.multiseries_id_columns = multiseries_id_columns

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

    def __eq__(self, other: CalendarFile) -> bool:  # type: ignore[override]
        """Compares the relevant fields of two calendars to assess equality"""
        vars1 = [self.__getattribute__(x) for x in [k.name for k in self._converter.keys]]
        vars2 = [other.__getattribute__(x) for x in [k.name for k in other._converter.keys]]
        return vars1 == vars2

    @classmethod
    def create(
        cls,
        file_path: str,
        calendar_name: Optional[str] = None,
        multiseries_id_columns: Optional[List[str]] = None,
    ) -> CalendarFile:
        """
        Creates a calendar using the given file. For information about calendar files, see the
        :ref:`calendar documentation <calendar-files>`

        The provided file must be a CSV in the format:

        .. code-block:: text

            Date,   Event,          Series ID,    Event Duration
            <date>, <event_type>,   <series id>,  <event duration>
            <date>, <event_type>,              ,  <event duration>

        A header row is required, and the "Series ID" and "Event Duration" columns are optional.

        Once the CalendarFile has been created, pass its ID with
        the :class:`DatetimePartitioningSpecification <datarobot.DatetimePartitioningSpecification>`
        when setting the target for a time series project in order to use it.

        Parameters
        ----------
        file_path : string
            A string representing a path to a local csv file.
        calendar_name : string, optional
            A name to assign to the calendar. Defaults to the name of the file if not provided.
        multiseries_id_columns : List[str] or None
            A list of the names of multiseries id columns to define which series an event
            belongs to. Currently only one multiseries id column is supported.

        Returns
        -------
        calendar_file : CalendarFile
            Instance with initialized data.

        Raises
        ------
        AsyncProcessUnsuccessfulError
            Raised if there was an error processing the provided calendar file.

        Examples
        --------
        .. code-block:: python

            # Creating a calendar with a specified name
            cal = dr.CalendarFile.create('/home/calendars/somecalendar.csv',
                                                     calendar_name='Some Calendar Name')
            cal.id
            >>> 5c1d4904211c0a061bc93013
            cal.name
            >>> Some Calendar Name

            # Creating a calendar without specifying a name
            cal = dr.CalendarFile.create('/home/calendars/somecalendar.csv')
            cal.id
            >>> 5c1d4904211c0a061bc93012
            cal.name
            >>> somecalendar.csv

            # Creating a calendar with multiseries id columns
            cal = dr.CalendarFile.create('/home/calendars/somemultiseriescalendar.csv',
                                         calendar_name='Some Multiseries Calendar Name',
                                         multiseries_id_columns=['series_id'])
            cal.id
            >>> 5da9bb21962d746f97e4daee
            cal.name
            >>> Some Multiseries Calendar Name
            cal.multiseries_id_columns
            >>> ['series_id']
        """

        # make sure it's a valid filename, and set the calendar name if not provided
        if isinstance(file_path, str) and os.path.isfile(file_path):
            if not calendar_name:
                calendar_name = os.path.basename(file_path)
        else:
            raise ValueError(f"The provided file does not exist: {file_path}")
        cls._validate_calendar_name(calendar_name)

        form_data = None
        if multiseries_id_columns:
            cls._validate_multiseries_id_columns(multiseries_id_columns)
            form_data = {"multiseries_id_columns": (None, json.dumps(multiseries_id_columns))}

        upload_response = cls._client.build_request_with_file(
            method="post",
            url=cls._upload_url,
            fname=calendar_name,
            file_path=file_path,
            form_data=form_data,
        )
        new_calendar_url = wait_for_async_resolution(
            cls._client, upload_response.headers["Location"]
        )

        return cls.from_location(new_calendar_url)

    @classmethod
    def create_calendar_from_dataset(
        cls,
        dataset_id: str,
        dataset_version_id: Optional[str] = None,
        calendar_name: Optional[str] = None,
        multiseries_id_columns: Optional[List[str]] = None,
        delete_on_error: Optional[bool] = False,
    ) -> CalendarFile:
        """
        Creates a calendar using the given dataset. For information about calendar files, see the
        :ref:`calendar documentation <calendar-files>`

        The provided dataset have the following format:

        .. code-block:: text

            Date,   Event,          Series ID,    Event Duration
            <date>, <event_type>,   <series id>,  <event duration>
            <date>, <event_type>,              ,  <event duration>

        The "Series ID" and "Event Duration" columns are optional.

        Once the CalendarFile has been created, pass its ID with
        the :class:`DatetimePartitioningSpecification <datarobot.DatetimePartitioningSpecification>`
        when setting the target for a time series project in order to use it.

        Parameters
        ----------
        dataset_id : string
            The identifier of the dataset from which to create the calendar.
        dataset_version_id : string, optional
            The identifier of the dataset version from which to create the calendar.
        calendar_name : string, optional
            A name to assign to the calendar. Defaults to the name of the dataset if not provided.
        multiseries_id_columns : list of Optional[str]
            A list of the names of multiseries id columns to define which series an event
            belongs to. Currently only one multiseries id column is supported.
        delete_on_error : boolean, optional
            Whether delete calendar file from Catalog if it's not valid.

        Returns
        -------
        calendar_file : CalendarFile
            Instance with initialized data.

        Raises
        ------
        AsyncProcessUnsuccessfulError
            Raised if there was an error processing the provided calendar file.

        Examples
        --------
        .. code-block:: python

            # Creating a calendar from a dataset
            dataset = dr.Dataset.create_from_file('/home/calendars/somecalendar.csv')
            cal = dr.CalendarFile.create_calendar_from_dataset(
                dataset.id, calendar_name='Some Calendar Name'
            )
            cal.id
            >>> 5c1d4904211c0a061bc93013
            cal.name
            >>> Some Calendar Name

            # Creating a calendar from a new dataset version
            new_dataset_version = dr.Dataset.create_version_from_file(
                dataset.id, '/home/calendars/anothercalendar.csv'
            )
            cal = dr.CalendarFile.create(
                new_dataset_version.id, dataset_version_id=new_dataset_version.version_id
            )
            cal.id
            >>> 5c1d4904211c0a061bc93012
            cal.name
            >>> anothercalendar.csv
        """
        if calendar_name is not None:
            cls._validate_calendar_name(calendar_name)

        payload: Dict[str, Union[Optional[str], bool, List[str]]] = {
            "name": calendar_name,
            "dataset_id": dataset_id,
            "dataset_version_id": dataset_version_id,
        }

        if delete_on_error:
            payload["delete_on_error"] = delete_on_error

        if multiseries_id_columns:
            cls._validate_multiseries_id_columns(multiseries_id_columns)
            payload["multiseries_id_columns"] = multiseries_id_columns

        generation_response = cls._client.post(
            cls._from_dataset_url, data=payload, headers={"Content-Type": "application/json"}
        )
        generated_calendar_url = wait_for_async_resolution(
            cls._client, generation_response.headers["Location"]
        )

        return cls.from_location(generated_calendar_url)

    @classmethod
    def create_calendar_from_country_code(
        cls, country_code: str, start_date: datetime, end_date: datetime
    ) -> CalendarFile:
        """
        Generates a calendar based on the provided country code and dataset start date and end
        dates. The provided country code should be uppercase and 2-3 characters long. See
        :meth:`CalendarFile.get_allowed_country_codes
        <datarobot.CalendarFile.get_allowed_country_codes>` for a list of allowed country codes.

        Parameters
        ----------
        country_code : string
            The country code for the country to use for generating the calendar.
        start_date : datetime.datetime
            The earliest date to include in the generated calendar.
        end_date : datetime.datetime
            The latest date to include in the generated calendar.

        Returns
        -------
        calendar_file : CalendarFile
            Instance with initialized data.
        """
        payload = {
            "countryCode": country_code,
            "startDate": start_date,
            "endDate": end_date,
        }
        generation_response = cls._client.post(
            cls._from_country_code_url, data=payload, headers={"Content-Type": "application/json"}
        )
        generated_calendar_url = wait_for_async_resolution(
            cls._client, generation_response.headers["Location"]
        )
        return cls.from_location(generated_calendar_url)

    @classmethod
    def get_allowed_country_codes(
        cls, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> List[CountryCode]:
        """
        Retrieves the list of allowed country codes that can be used for generating the preloaded
        calendars.

        Parameters
        ----------
        offset : int
            Optional, defaults to 0. This many results will be skipped.
        limit : int
            Optional, defaults to 100, maximum 1000. At most this many results are returned.

        Returns
        -------
        list
            A list dicts, each of which represents an allowed country codes. Each item has the
            following structure:

            * ``name`` : (str) The name of the country.
            * ``code`` : (str) The code for this country. This is the value that should be supplied
              to :meth:`CalendarFile.create_calendar_from_country_code
              <datarobot.CalendarFile.create_calendar_from_country_code>`.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return list(unpaginate(cls._allowed_countries_list_url, params, cls._client))

    @classmethod
    def get(cls, calendar_id: str) -> CalendarFile:
        """
        Gets the details of a calendar, given the id.

        Parameters
        ----------
        calendar_id : str
            The identifier of the calendar.

        Returns
        -------
        calendar_file : CalendarFile
            The requested calendar.

        Raises
        ------
        DataError
            Raised if the calendar_id is invalid, i.e. the specified CalendarFile does not exist.

        Examples
        --------
        .. code-block:: python

            cal = dr.CalendarFile.get(some_calendar_id)
            cal.id
            >>> some_calendar_id
        """
        return cls.from_location(cls._calendar_url.format(calendar_id))

    @classmethod
    def list(
        cls, project_id: Optional[str] = None, batch_size: Optional[int] = None
    ) -> List[CalendarFile]:
        """
        Gets the details of all calendars this user has view access for.

        Parameters
        ----------
        project_id : Optional[str]
            If provided, will filter for calendars associated only with the specified project.
        batch_size : Optional[int]
            The number of calendars to retrieve in a single API call. If specified, the client may
            make multiple calls to retrieve the full list of calendars. If not specified, an
            appropriate default will be chosen by the server.

        Returns
        -------
        calendar_list : list of :class:`CalendarFile <datarobot.CalendarFile>`
            A list of CalendarFile objects.

        Examples
        --------
        .. code-block:: python

            calendars = dr.CalendarFile.list()
            len(calendars)
            >>> 10
        """
        if project_id is not None:
            list_url = cls._base_url + f"?projectId={project_id}"
        else:
            list_url = cls._base_url

        params = {}
        if batch_size is not None:
            params["limit"] = batch_size

        return [cls.from_server_data(entry) for entry in unpaginate(list_url, params, cls._client)]

    @classmethod
    def delete(cls, calendar_id: str) -> None:
        """
        Deletes the calendar specified by calendar_id.

        Parameters
        ----------
        calendar_id : str
            The id of the calendar to delete.
            The requester must have OWNER access for this calendar.

        Raises
        ------
        ClientError
            Raised if an invalid calendar_id is provided.

        Examples
        --------
        .. code-block:: python

            # Deleting with a valid calendar_id
            status_code = dr.CalendarFile.delete(some_calendar_id)
            status_code
            >>> 204
            dr.CalendarFile.get(some_calendar_id)
            >>> ClientError: Item not found
        """
        cls._client.delete(cls._calendar_url.format(calendar_id))

    @classmethod
    def update_name(cls, calendar_id: str, new_calendar_name: str) -> int:
        """
        Changes the name of the specified calendar to the specified name.
        The requester must have at least READ_WRITE permissions on the calendar.

        Parameters
        ----------
        calendar_id : str
            The id of the calendar to update.
        new_calendar_name : str
            The new name to set for the specified calendar.

        Returns
        -------
        status_code : int
            200 for success

        Raises
        ------
        ClientError
            Raised if an invalid calendar_id is provided.

        Examples
        --------
        .. code-block:: python

            response = dr.CalendarFile.update_name(some_calendar_id, some_new_name)
            response
            >>> 200
            cal = dr.CalendarFile.get(some_calendar_id)
            cal.name
            >>> some_new_name

        """
        cls._validate_calendar_name(new_calendar_name)

        response_data: Response = cls._client.patch(
            cls._calendar_url.format(calendar_id), data={"name": new_calendar_name}
        )
        return response_data.status_code

    @classmethod
    def share(cls, calendar_id: str, access_list: List[SharingAccess]) -> int:
        """
        Shares the calendar with the specified users, assigning the specified roles.

        Parameters
        ----------
        calendar_id : str
            The id of the calendar to update
        access_list:
            A list of dr.SharingAccess objects. Specify `None` for the role to delete a user's
            access from the specified CalendarFile. For more information on specific access levels,
            see the :ref:`sharing <sharing>` documentation.

        Returns
        -------
        status_code : int
            200 for success

        Raises
        ------
        ClientError
            Raised if unable to update permissions for a user.
        AssertionError
            Raised if access_list is invalid.

        Examples
        --------
        .. code-block:: python

            # assuming some_user is a valid user, share this calendar with some_user
            sharing_list = [dr.SharingAccess(some_user_username,
                                             dr.enums.SHARING_ROLE.READ_WRITE)]
            response = dr.CalendarFile.share(some_calendar_id, sharing_list)
            response.status_code
            >>> 200

            # delete some_user from this calendar, assuming they have access of some kind already
            delete_sharing_list = [dr.SharingAccess(some_user_username,
                                                    None)]
            response = dr.CalendarFile.share(some_calendar_id, delete_sharing_list)
            response.status_code
            >>> 200

            # Attempt to add an invalid user to a calendar
            invalid_sharing_list = [dr.SharingAccess(invalid_username,
                                                     dr.enums.SHARING_ROLE.READ_WRITE)]
            dr.CalendarFile.share(some_calendar_id, invalid_sharing_list)
            >>> ClientError: Unable to update access for this calendar

        """
        # ensure access_list is a list
        assert isinstance(access_list, list), "access_list must be a list"
        # ensure each item in access_list is a SharingAccess object
        assert all(
            isinstance(access, SharingAccess) for access in access_list
        ), "access_list must be a list of dr.SharingAccess objects"

        payload = {"users": [access.collect_payload() for access in access_list]}
        response_data: Response = cls._client.patch(
            cls._access_control_url.format(calendar_id), data=payload, keep_attrs={"role"}
        )
        return response_data.status_code

    @classmethod
    def get_access_list(
        cls, calendar_id: str, batch_size: Optional[int] = None
    ) -> List[SharingAccess]:
        """
        Retrieve a list of users that have access to this calendar.

        Parameters
        ----------
        calendar_id : str
            The id of the calendar to retrieve the access list for.
        batch_size : Optional[int]
            The number of access records to retrieve in a single API call. If specified, the client
            may make multiple calls to retrieve the full list of calendars. If not specified, an
            appropriate default will be chosen by the server.

        Returns
        -------
        access_control_list : list of :class:`SharingAccess <datarobot.SharingAccess>`
            A list of :class:`SharingAccess <datarobot.SharingAccess>` objects.

        Raises
        ------
        ClientError
            Raised if user does not have access to calendar or calendar does not exist.
        """

        params = {}
        if batch_size is not None:
            params["limit"] = batch_size
        url = cls._access_control_url.format(calendar_id)
        return [
            SharingAccess.from_server_data(datum) for datum in unpaginate(url, params, cls._client)
        ]

    @classmethod
    def _validate_calendar_name(cls, calendar_name: str) -> None:
        if not isinstance(calendar_name, str):
            raise ValueError("Invalid calendar name, only strings are supported")
        try:
            calendar_name.encode("ascii")
        # Which exception we get here depends on whether the input was string or unicode
        # (we allow both).
        except (UnicodeEncodeError, UnicodeDecodeError):
            raise errors.IllegalFileName

    @classmethod
    def _validate_multiseries_id_columns(cls, multiseries_id_columns: Iterable[str]) -> None:
        if not isinstance(multiseries_id_columns, (list, tuple)):
            raise ValueError(
                "Expected list of str for multiseries_id_columns, got: {}".format(
                    multiseries_id_columns
                )
            )
