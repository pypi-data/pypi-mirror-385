#
# Copyright 2023-2025 DataRobot, Inc. and its affiliates.
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

from typing import Any, List, Optional, Union

import trafaret as t

from datarobot.enums import PlaygroundType, enum_to_list
from datarobot.models.api_object import APIObject
from datarobot.models.use_cases.use_case import UseCase
from datarobot.models.use_cases.utils import UseCaseLike, get_use_case_id, resolve_use_cases
from datarobot.utils.pagination import unpaginate

playground_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String(allow_blank=True),
        t.Key("description"): t.String(allow_blank=True),
        t.Key("use_case_id"): t.String,
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
        t.Key("last_update_date"): t.String,
        t.Key("last_update_user_id"): t.String,
        t.Key("saved_llm_blueprints_count"): t.Int,
        t.Key("llm_blueprints_count"): t.Int,
        t.Key("user_name"): t.String(allow_blank=True),
        t.Key("playground_type"): t.Enum(*enum_to_list(PlaygroundType)),
    }
).ignore_extra("*")


copy_insights_request_trafaret = t.Dict(
    {
        t.Key("source_playground_id"): t.String,
        t.Key("with_evaluation_datasets"): t.Bool,
    }
).ignore_extra("*")


class CopyInsightsRequest(APIObject):
    """
    The copy insights from an existing playground request.

    Attributes
    ----------
    source_playground_id : str
        The ID of the existing playground from where to copy insights.
    with_evaluation_datasets : bool
        If `true` also copies source playground evaluation datasets to target playground.
    """

    _converter = copy_insights_request_trafaret

    def __init__(self, source_playground_id: str, with_evaluation_datasets: bool = False):
        self.source_playground_id = source_playground_id
        self.with_evaluation_datasets = with_evaluation_datasets

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_playground_id": self.source_playground_id,
            "with_evaluation_datasets": self.with_evaluation_datasets,
        }


class Playground(APIObject):
    """
    Metadata for a DataRobot GenAI playground.

    Attributes
    ----------
    id : str
        Playground ID.
    name : str
        Playground name.
    description : str
        Description of the playground.
    use_case_id : str
        Linked use case ID.
    creation_date : str
        The date when the playground was created.
    creation_user_id : str
        ID of the creating user.
    last_update_date : str
        Date when the playground was most recently updated.
    last_update_user_id : str
        ID of the user who most recently updated the playground.
    saved_llm_blueprints_count : int
        Number of saved LLM blueprints in the playground.
    llm_blueprints_count : int
        Number of LLM blueprints in the playground.
    user_name : str
        The name of the user who created the playground.
    playground_type : Optional[PlaygroundType]
    """

    _path = "api/v2/genai/playgrounds"

    _converter = playground_trafaret

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        use_case_id: str,
        creation_date: str,
        creation_user_id: str,
        last_update_date: str,
        last_update_user_id: str,
        saved_llm_blueprints_count: int,
        llm_blueprints_count: int,
        user_name: str,
        playground_type: Optional[PlaygroundType] = PlaygroundType.RAG,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.use_case_id = use_case_id
        self.creation_date = creation_date
        self.creation_user_id = creation_user_id
        self.last_update_date = last_update_date
        self.last_update_user_id = last_update_user_id
        self.saved_llm_blueprints_count = saved_llm_blueprints_count
        self.llm_blueprints_count = llm_blueprints_count
        self.user_name = user_name
        self.playground_type = playground_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        use_case: Optional[Union[UseCase, str]] = None,
        copy_insights: Optional[CopyInsightsRequest] = None,
        playground_type: Optional[PlaygroundType] = PlaygroundType.RAG,
    ) -> Playground:
        """
        Create a new playground.

        Parameters
        ----------
        name : str
            Playground name.
        description : Optional[str]
            Description of the playground, by default "".
        use_case : Optional[Union[UseCase, str]], optional
            Use case to link to the created playground.
        copy_insights: CopyInsightsRequest, optional
            If present, copies insights from the source playground to the created playground.

        Returns
        -------
        playground : Playground
            The created playground.
        """
        payload = {
            "name": name,
            "description": description,
            "use_case_id": get_use_case_id(use_case, is_required=True),
            "copy_insights": copy_insights.to_dict() if copy_insights is not None else None,
            "playground_type": playground_type,
        }
        url = f"{cls._client.domain}/{cls._path}/"
        r_data = cls._client.post(url, data=payload)
        return cls.from_server_data(r_data.json())

    @classmethod
    def get(cls, playground_id: str) -> Playground:
        """
        Retrieve a single playground.

        Parameters
        ----------
        playground_id : str
            The ID of the playground you want to retrieve.

        Returns
        -------
        playground : Playground
            The requested playground.
        """
        url = f"{cls._client.domain}/{cls._path}/{playground_id}/"
        r_data = cls._client.get(url)
        return cls.from_server_data(r_data.json())

    @classmethod
    def list(
        cls,
        use_case: Optional[UseCaseLike] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Playground]:
        """
        List all playgrounds available to the user. If the use_case is specified or can be
        inferred from the Context then the results are restricted to the playgrounds
        associated with the UseCase.

        Parameters
        ----------
        use_case : Optional[UseCaseLike], optional
            The returned playgrounds are filtered to those associated with a specific Use Case
            or Cases if specified or can be inferred from the Context.
            Accepts either the entity or the ID.
        search : Optional[str]
            String for filtering playgrounds.
            Playgrounds that contain the string in name will be returned.
            If not specified, all playgrounds will be returned.
        sort : Optional[str]
            Property to sort playgrounds by.
            Prefix the attribute name with a dash to sort in descending order,
            e.g. sort='-creationDate'.
            Currently supported options are listed in ListPlaygroundsSortQueryParams
            but the values can differ with different platform versions.
            By default, the sort parameter is None which will result in
            playgrounds being returned in order of creation time descending.

        Returns
        -------
        playgrounds : list[Playground]
            A list of playgrounds available to the user.
        """
        params = {
            "search": search,
            "sort": sort,
        }
        params = resolve_use_cases(use_cases=use_case, params=params, use_case_key="use_case_id")
        url = f"{cls._client.domain}/{cls._path}/"
        r_data = unpaginate(url, params, cls._client)
        return [cls.from_server_data(data) for data in r_data]

    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> Playground:
        """
        Update the playground.

        Parameters
        ----------
        name : str
            The new name for the playground.
        description: str
            The new description for the playground.

        Returns
        -------
        playground : Playground
            The updated playground.
        """
        payload = {"name": name, "description": description}
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        r_data = self._client.patch(url, data=payload)
        return self.from_server_data(r_data.json())

    def delete(self) -> None:
        """
        Delete the playground.
        """
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        self._client.delete(url)
