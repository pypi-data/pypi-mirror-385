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

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type, TypeVar, Union

from strenum import StrEnum
import trafaret as t

from datarobot.models.api_object import APIObject, ServerDataType
from datarobot.utils import from_api
from datarobot.utils.pagination import unpaginate

TOCRJobResource = TypeVar("TOCRJobResource", bound="OCRJobResource")


class OCRJobDatasetLanguage(Enum):
    """Supported OCR language"""

    ENGLISH = auto()
    JAPANESE = auto()

    @classmethod
    def from_string(cls, language_str: str) -> "OCRJobDatasetLanguage":
        for language in cls:
            if language_str == language.name:
                return language
        msg = (
            f"Language str {language_str} is invalid. "
            f"Valid values are {[lang.name for lang in cls]}"
        )
        raise ValueError(msg)


class DataRobotOCREngineType(StrEnum):
    """Supported OCR engine type"""

    TESSERACT = auto()
    ARYN = auto()


class DataRobotArynOutputFormat(StrEnum):
    """Supported ARYN OCR engine output format"""

    JSON = auto()
    MARKDOWN = auto()


def from_language_enum_to_api_representation(lang_enum: OCRJobDatasetLanguage) -> str:
    """Convert OCRJobDatasetLanguage to API representation.

    Parameters
    ----------
    lang_enum: OCRJobDatasetLanguage
        language enum

    Returns
    -------
    str
        OCRJobDatasetLanguage API representation
    """
    return lang_enum.name


class OCRJobStatusEnum(Enum):
    """OCR Job status enum"""

    EXECUTING = auto()
    FAILURE = auto()
    PENDING = auto()
    STOPPED = auto()
    SUCCESS = auto()
    UNKNOWN = auto()


def from_api_representation_to_job_status_enum(status_api_representation: str) -> OCRJobStatusEnum:
    """Convert OCR job status API representation to OCRJobStatusEnum.

    Parameters
    ----------
    status_api_representation: str
        OCR job status API representation

    Returns
    -------
    OCRJobStatusEnum
        OCR job status enum

    Raises
    ------
    ValueError
        Raised when status_api_representation is invalid
    """
    if not status_api_representation.islower():
        raise ValueError("Status api representation must be lowercase.")
    for status in list(OCRJobStatusEnum):
        if status_api_representation == status.name.lower():
            return status
    msg = (
        f"Status str {status_api_representation} is invalid. "
        f"Valid values are {[status.name.lower() for status in list(OCRJobStatusEnum)]}"
    )
    raise ValueError(msg)


@dataclass
class StartOCRJobResponse:
    """Container of Start OCR Job API response"""

    job_status_location: str
    output_location: str
    error_report_location: str

    @classmethod
    def from_server_data(cls, data: ServerDataType) -> "StartOCRJobResponse":
        return cls(
            job_status_location=data["jobStatusLocation"],  # type: ignore[call-overload]
            output_location=data["outputLocation"],  # type: ignore[call-overload]
            error_report_location=data["errorReportLocation"],  # type: ignore[call-overload]
        )


_engine_specific_parameters_converter = t.Dict(
    {
        t.Key("engine_type", optional=True): t.Or(
            t.Enum(*[e.name for e in DataRobotOCREngineType]), t.Null()
        ),
        t.Key("output_format", optional=True): t.Or(
            t.Enum(*[f.name for f in DataRobotArynOutputFormat]), t.Null()
        ),
    }
).ignore_extra("*")


class OCREngineSpecificParameters:
    """Container of Engine Specific Parameters. It is used to specify required
    OCR engine parameters when creating an OCR job resource.

    .. versionadded:: v3.8.0

    Attributes
    ----------
    engine_type: str
        Optional. String representation of DataRobotOCREngineType.
    output_format: str
        Optional. String representation of DataRobotArynOutputFormat when engine type is ARYN.
    """

    def __init__(self, engine_type: Optional[str] = None, output_format: Optional[str] = None):
        _engine_specific_parameters_converter.check(
            {
                "engine_type": engine_type,
                "output_format": output_format,
            }
        )
        self.engine_type = engine_type
        self.output_format = output_format

    def get_payload(self) -> Dict[str, Optional[str]]:
        """return dict containing engine specific parameters whose values are not None"""
        data = {
            "engine_type": self.engine_type,
            "output_format": self.output_format,
        }
        return {key: value for key, value in data.items() if value}


class OCRJobResource(APIObject):
    """An OCR job resource container. It is used to:
    - Get an existing OCR  job resource.
    - List available OCR job resources.
    - Start an OCR job.
    - Check the status of a started OCR job.
    - Download the error report of a started OCR job.

    .. versionadded:: v3.6.0b0

    Attributes
    ----------
    id: str
        The identifier of an OCR job resource.
    input_catalog_id: str
        The identifier of an AI catalog item used as the OCR job input.
    output_catalog_id: str
        The identifier of an AI catalog item used as the OCR job output.
    user_id: str
        The identifier of a user.
    job_started: bool
        Determines if a job associated with the OCRJobResource has started.
    language: str
        String representation of OCRJobDatasetLanguage.
    engine_specific_parameters: OCREngineSpecificParameters
        Optional. OCR engine parameters.

    """

    _path = "ocrJobResources/"

    _converter = t.Dict(
        {
            t.Key("id"): t.String(),
            t.Key("input_catalog_id"): t.String(),
            t.Key("output_catalog_id"): t.String(),
            t.Key("user_id"): t.String(),
            t.Key("job_started"): t.Bool(),
            t.Key("language"): t.Enum(*[el.name for el in OCRJobDatasetLanguage]),
            t.Key(
                "engine_specific_parameters", optional=True
            ): _engine_specific_parameters_converter,
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(
        self,
        id: str,
        input_catalog_id: str,
        output_catalog_id: str,
        user_id: str,
        job_started: bool,
        language: str,
        engine_specific_parameters: Optional[OCREngineSpecificParameters] = None,
    ) -> None:
        self.id = id
        self.input_catalog_id = input_catalog_id
        self.output_catalog_id = output_catalog_id
        self.user_id = user_id
        self.job_started = job_started
        self.language = OCRJobDatasetLanguage.from_string(language)
        self.engine_specific_parameters = engine_specific_parameters

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id!r})"

    @classmethod
    def get(cls, job_resource_id: str) -> "OCRJobResource":
        """Get an OCR job resource.

        Parameters
        ----------
        job_resource_id: str
            identifier of OCR job resource

        Returns
        -------
        OCRJobResource
            returned OCR job resource
        """
        path = f"{cls._path}{job_resource_id}/"
        data = cls._client.get(path).json()
        return cls.from_server_data(data)

    @classmethod
    def list(cls, offset: int = 0, limit: int = 10) -> List["OCRJobResource"]:
        """Get a list of OCR job resources.

        Parameters
        ----------
        offset: int
            The offset of the query.
        limit: int
            The limit of returned OCR job resources.

        Returns
        -------
        List[OCRJobResource]
            A list of OCR job resources.
        """
        query_params = {"offset": offset, "limit": limit}
        list_of_job_resources = unpaginate(cls._path, query_params, cls._client)
        return [
            OCRJobResource.from_server_data(job_resource) for job_resource in list_of_job_resources
        ]

    @classmethod
    def create(
        cls,
        input_catalog_id: str,
        language: OCRJobDatasetLanguage,
        engine_specific_parameters: Optional[OCREngineSpecificParameters] = None,
    ) -> "OCRJobResource":
        """Create a new OCR job resource and return it.

        Parameters
        ----------
        input_catalog_id: str
            The identifier of an AI catalog item used as the OCR job input.
        language: OCRJobDatasetLanguage
            The OCR job dataset language.
        engine_specific_parameters: OCREngineSpecificParameters
            Optional. OCR engine parameters.

        Returns
        -------
        OCRJobResource
            The created OCR job resource.
        """
        request_body: Dict[str, Union[Optional[str], dict[str, Optional[str]]]] = {
            "dataset_id": input_catalog_id,
            "language": from_language_enum_to_api_representation(language),
        }
        if engine_specific_parameters and engine_specific_parameters.get_payload():
            request_body["engine_specific_parameters"] = engine_specific_parameters.get_payload()

        data = cls._client.post(
            cls._path,
            data=request_body,
            headers={"Content-type": "application/json"},
        ).json()
        return cls.from_server_data(data)

    def start_job(self) -> StartOCRJobResponse:
        """Start an OCR job with this OCR job resource.

        Returns
        -------
        StartOCRJobResponse
            The response of starting an OCR job.
        """
        data = self._client.post(f"{self._path}{self.id}/start/").json()
        return StartOCRJobResponse.from_server_data(data)

    def get_job_status(self) -> OCRJobStatusEnum:
        """Get status of the OCR job associated with this OCR job resource.

        Returns
        -------
        OCRJobStatusEnum
            OCR job status enum
        """
        path = f"{self._path}{self.id}/jobStatus/"
        data = self._client.get(path).json()

        return from_api_representation_to_job_status_enum(data["jobStatus"])

    def download_error_report(self, download_file_path: Path) -> None:
        """Download the error report of the OCR job associated with this OCR job resource.

        Parameters
        ----------
        download_file_path: Path
            path to download error report

        Returns
        -------
        None
        """
        path = f"{self._path}{self.id}/errorReport/"
        response = self._client.get(path, stream=True)
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            download_file_path.write_bytes(chunk)

    @classmethod
    def from_server_data(
        cls: Type[TOCRJobResource],
        data: ServerDataType,
        keep_attrs: Optional[Iterable[str]] = None,
    ) -> TOCRJobResource:
        converted_data = cls._converter.check(from_api(data))
        params = converted_data.pop("engine_specific_parameters", None)
        if params:
            converted_data["engine_specific_parameters"] = OCREngineSpecificParameters(**params)
        return cls(**converted_data)
