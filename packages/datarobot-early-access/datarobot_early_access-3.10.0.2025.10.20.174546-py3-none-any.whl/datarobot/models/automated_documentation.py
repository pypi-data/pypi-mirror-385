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
from typing import List, Optional, Tuple, cast

from requests import Response
import trafaret as t
from typing_extensions import TypedDict

from datarobot._compat import String
from datarobot.enums import DEFAULT_MAX_WAIT, DocumentType, Locales
from datarobot.models.api_object import APIObject
from datarobot.utils import camelize, deprecation, from_api, get_id_from_location, parse_time
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


class DocumentOption(TypedDict):
    document_type: DocumentType
    locale: Locales


class AutomatedDocument(APIObject):
    """
    An automated documentation object.

    .. versionadded:: v2.24

    Attributes
    ----------
    document_type : str or None
        Type of automated document. You can specify: ``MODEL_COMPLIANCE``, ``AUTOPILOT_SUMMARY``
        depending on your account settings. Required for document generation.
    entity_id : str or None
        ID of the entity to generate the document for. It can be model ID or project ID.
        Required for document generation.
    output_format : str or None
        Format of the generate document, either ``docx`` or ``html``.
        Required for document generation.
    locale : str or None
        Localization of the document, dependent on your account settings.
        Default setting is ``EN_US``.
    template_id : str or None
        Template ID to use for the document outline. Defaults to standard DataRobot template.
        See the documentation for :py:class:`ComplianceDocTemplate
        <datarobot.models.compliance_doc_template.ComplianceDocTemplate>` for more information.
    id :  str or None
        ID of the document. Required to download or delete a document.
    filepath : str or None
        Path to save a downloaded document to. Either include a file path and name or the file
        will be saved to the directory from which the script is launched.
    created_at :  datetime or None
        Document creation timestamp.

    """

    DEFAULT_BATCH_SIZE = 100

    _path = "automatedDocuments/"
    _model_compliance_initialization_path = "modelComplianceDocsInitializations/"

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("created_at"): parse_time,
            t.Key("entity_id"): String(),
            t.Key("output_format"): String(),
            t.Key("locale"): String(),
            t.Key("document_type"): String(),
            t.Key("template_id", optional=True): t.Or(String(), t.Null()),
        }
    ).allow_extra("*")

    def __init__(
        self,
        entity_id: Optional[str] = None,
        document_type: Optional[str] = None,
        output_format: Optional[str] = None,
        locale: Optional[str] = None,
        template_id: Optional[str] = None,
        id: Optional[str] = None,
        filepath: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.entity_id = entity_id
        self.document_type = document_type
        self.output_format = output_format
        self.locale = locale
        self.template_id = template_id
        self.id = id
        self.filepath = filepath
        self.created_at = created_at

    @classmethod
    @deprecation.deprecated(
        deprecated_since_version="v3.5",
        will_remove_version="v3.6",
        message=(
            "This method is deprecated, "
            "please use 'datarobot.AutomatedDocument.list_all_available_document_types' instead."
        ),
    )
    def list_available_document_types(cls) -> List[DocumentOption]:
        """
        Get a list of all available document types and locales. This method is deprecated.

        Returns
        -------
        List[DocumentOption]
          {"data": List of dicts}

        Examples
        --------
        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            doc_types = dr.AutomatedDocument.list_available_document_types()

        """

        response = cls._client.get("automatedDocumentOptions/")
        return cast(List[DocumentOption], from_api(response.json()))

    @classmethod
    def list_all_available_document_types(cls) -> List[DocumentOption]:
        """
        Get a list of all available document types and locales.
        This method is direct replacement of `list_available_document_types()`.

        Returns
        -------
        List of dicts

        Examples
        --------
        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            doc_types = dr.AutomatedDocument.list_all_available_document_types()

        """
        response = cls._client.get("automatedDocumentOptions/")
        return cast(List[DocumentOption], from_api(response.json()["data"]))

    @property
    def is_model_compliance_initialized(self) -> Tuple[bool, str]:
        """Check if model compliance documentation pre-processing is initialized.
        Model compliance documentation pre-processing must be initialized before
        generating documentation for a custom model.

        Returns
        -------
        Tuple of (boolean, string)
            - `boolean` flag is whether model compliance documentation pre-processing is initialized
            - `string` value is the initialization status
        """
        return self._model_compliance_initialization_status(
            f"{self._model_compliance_initialization_path}{self.entity_id}/"
        )

    def initialize_model_compliance(self) -> Tuple[bool, str]:
        """Initialize model compliance documentation pre-processing.
        Must be called before generating documentation for a custom model.

        Returns
        -------
        Tuple of (boolean, string)
            - `boolean` flag is whether model compliance documentation pre-processing is initialized
            - `string` value is the initialization status

        Examples
        --------
        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)

            # NOTE: entity_id is either a model id or a model package (version) id
            doc = dr.AutomatedDocument(
                    document_type="MODEL_COMPLIANCE",
                    entity_id="6f50cdb77cc4f8d1560c3ed5",
                    output_format="docx",
                    locale="EN_US")

            doc.initialize_model_compliance()

        """

        response = self._client.post(
            f"{self._model_compliance_initialization_path}{self.entity_id}/"
        )
        location = wait_for_async_resolution(self._client, response.headers["Location"])
        return self._model_compliance_initialization_status(location)

    def generate(self, max_wait: int = DEFAULT_MAX_WAIT) -> Response:
        """Request generation of an automated document.

        Required attributes to request document generation: ``document_type``, ``entity_id``,
        and ``output_format``.

        Returns
        -------
        :class:`requests.models.Response`

        Examples
        --------
        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)

            doc = dr.AutomatedDocument(
                    document_type="MODEL_COMPLIANCE",
                    entity_id="6f50cdb77cc4f8d1560c3ed5",
                    output_format="docx",
                    locale="EN_US",
                    template_id="50efc9db8aff6c81a374aeec",
                    filepath="/Users/username/Documents/example.docx"
                    )

            doc.generate()
            doc.download()

        """
        payload = {
            "entity_id": self.entity_id,
            "document_type": self.document_type,
            "output_format": self.output_format,
            "locale": self.locale,
            "template_id": self.template_id,
        }
        payload = {key: val for key, val in payload.items() if val is not None}

        response = self._client.post(self._path, data=payload)
        location = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )
        self.id = get_id_from_location(location)

        return cast(Response, response)

    def download(self) -> Response:
        """
        Download a generated Automated Document.
        Document ID is required to download a file.

        Returns
        -------
        :class:`requests.models.Response`

        Examples
        --------

        Generating and downloading the generated document:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)

            doc = dr.AutomatedDocument(
                    document_type="AUTOPILOT_SUMMARY",
                    entity_id="6050d07d9da9053ebb002ef7",
                    output_format="docx",
                    filepath="/Users/username/Documents/Project_Report_1.docx"
                    )

            doc.generate()
            doc.download()

        Downloading an earlier generated document when you know the document ID:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            doc = dr.AutomatedDocument(id='5e8b6a34d2426053ab9a39ed')
            doc.download()

        Notice that ``filepath`` was not set for this document. In this case, the file is saved
        to the directory from which the script was launched.

        Downloading a document chosen from a list of earlier generated documents:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)

            model_id = "6f5ed3de855962e0a72a96fe"
            docs = dr.AutomatedDocument.list_generated_documents(entity_ids=[model_id])
            doc = docs[0]
            doc.filepath = "/Users/me/Desktop/Recommended_model_doc.docx"
            doc.download()

        """
        if not self.id:
            raise AttributeError(
                "Document ID not provided. Assign it to AutomatedDocument object `id` attribute."
            )
        response = self._client.get(f"{self._path}{self.id}/", stream=True)

        if not self.filepath:
            self.filepath = response.headers["Content-Disposition"].split("=")[-1]

        with open(cast(str, self.filepath), mode="wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

        return cast(Response, response)

    def delete(self) -> Response:
        """
        Delete a document using its ID.

        Returns
        -------
        :class:`requests.models.Response`

        Examples
        --------

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            doc = dr.AutomatedDocument(id="5e8b6a34d2426053ab9a39ed")
            doc.delete()

        If you don't know the document ID, you can follow the same workflow to get the ID as in
        the examples for the ``AutomatedDocument.download`` method.


        """
        if not self.id:
            raise AttributeError(
                "Provide Document ID to delete a document."
                "Assign it to AutomatedDocument object `id` attribute or pass to class constructor."
            )

        return cast(Response, self._client.delete(f"{self._path}{self.id}/"))

    @classmethod
    def list_generated_documents(
        cls,
        document_types: Optional[List[str]] = None,
        entity_ids: Optional[List[str]] = None,
        output_formats: Optional[List[str]] = None,
        locales: Optional[List[str]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List["AutomatedDocument"]:
        """
        Get information about all previously generated documents available for your account. The
        information includes document ID and type, ID of the entity it was generated for, time of
        creation, and other information.

        Parameters
        ----------
        document_types : List of str or None
            Query for one or more document types.
        entity_ids : List of str or None
            Query generated documents by one or more entity IDs.
        output_formats : List of str or None
            Query for one or more output formats.
        locales : List of str or None
            Query generated documents by one or more locales.
        offset: int or None
            Number of items to skip. Defaults to 0 if not provided.
        limit: int or None
            Number of items to return, maximum number of items is 1000.

        Returns
        -------
        List of AutomatedDocument objects, where each object contains attributes described in
        :py:class:`AutomatedDocument<datarobot.models.automated_documentation.AutomatedDocument>`

        Examples
        --------

        To get a list of all generated documents:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            docs = AutomatedDocument.list_generated_documents()

        To get a list of all ``AUTOPILOT_SUMMARY`` documents:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            docs = AutomatedDocument.list_generated_documents(document_types=["AUTOPILOT_SUMMARY"])

        To get a list of 5 recently created automated documents in ``html`` format:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            docs = AutomatedDocument.list_generated_documents(output_formats=["html"], limit=5)

        To get a list of automated documents created for specific entities (projects or models):

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)
            docs = AutomatedDocument.list_generated_documents(
                entity_ids=["6051d3dbef875eb3be1be036",
                            "6051d3e1fbe65cd7a5f6fde6",
                            "6051d3e7f86c04486c2f9584"]
                )

        Note, that the list of results contains ``AutomatedDocument`` objects, which means that you
        can execute class-related methods on them. Here's how you can list, download, and then
        delete from the server all automated documents related to a certain entity:

        .. code-block:: python

            import datarobot as dr

            dr.Client(token=my_token, endpoint=endpoint)

            ids = ["6051d3dbef875eb3be1be036", "5fe1d3d55cd810ebdb60c517f"]
            docs = AutomatedDocument.list_generated_documents(entity_ids=ids)
            for doc in docs:
                doc.download()
                doc.delete()
        """
        params = {
            "document_type": document_types,
            "entity_id": entity_ids,
            "output_format": output_formats,
            "locale": locales,
            "offset": offset,
            "limit": limit,
        }
        params = {camelize(key): val for key, val in params.items() if val is not None}

        if not limit:
            params["limit"] = cls.DEFAULT_BATCH_SIZE
            return [
                cls.from_server_data(item) for item in unpaginate(cls._path, params, cls._client)
            ]

        items = cls._client.get(cls._path, params=params).json()["data"]
        return [cls.from_server_data(item) for item in items]

    def _model_compliance_initialization_status(self, location: str) -> Tuple[bool, str]:
        response = self._client.get(location)
        data = response.json()
        return data["initialized"], data["status"]

    def __repr__(self) -> str:
        attrs = ", ".join(item[0] + "=" + str(item[1]) for item in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
