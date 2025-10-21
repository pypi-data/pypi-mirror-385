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

from typing import Any, Dict, List, Optional, Union

import trafaret as t

from datarobot.errors import ClientError
from datarobot.models.api_object import APIObject
from datarobot.models.deployment import Deployment
from datarobot.models.genai.playground import Playground
from datarobot.models.model import Model
from datarobot.models.use_cases.use_case import UseCase
from datarobot.models.use_cases.utils import UseCaseLike, get_use_case_id, resolve_use_cases
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


def get_entity_id(entity: Union[CustomModelValidation, Deployment, Model, Playground, str]) -> str:
    """
    Get the entity ID from the entity parameter.

    Parameters
    ----------
    entity : APIObject or str
        Specifies either the entity ID or the entity.

    Returns
    -------
    id : str
        The entity ID.
    """
    return entity if isinstance(entity, str) else entity.id


custom_model_validation_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String(allow_blank=True),
        t.Key("prompt_column_name"): t.String,
        t.Key("target_column_name"): t.String,
        t.Key("deployment_id"): t.String,
        t.Key("validation_status"): t.String,
        t.Key("model_id"): t.String,
        t.Key("deployment_access_data", optional=True, default=None): t.Or(
            t.Null,
            t.Dict(
                {
                    t.Key("prediction_api_url"): t.String,
                    t.Key("datarobot_key", optional=True, default=None): t.Or(t.Null, t.String),
                    t.Key("authorization_header"): t.String,
                    t.Key("input_type"): t.String,
                    t.Key("model_type"): t.String,
                }
            ).ignore_extra("*"),
        ),
        t.Key("tenant_id"): t.String,
        t.Key("user_id"): t.String,
        t.Key("creation_date"): t.String,
        t.Key("error_message", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("deployment_name", optional=True, default=None): t.Or(
            t.Null, t.String(allow_blank=True)
        ),
        t.Key("user_name", optional=True, default=None): t.Or(t.Null, t.String(allow_blank=True)),
        t.Key("use_case_id", optional=True, default=None): t.Or(t.Null, t.String),
        t.Key("prediction_timeout"): t.Int,
    }
).ignore_extra("*")


class CustomModelValidation(APIObject):
    """
    The validation record checking the ability of the deployment to serve
    as a custom model LLM, custom model vector database, or custom model embedding.

    Attributes
    ----------
    id : str
        The ID of the validation.
    prompt_column_name : str
        The name of the column the deployed model uses for prompt text input.
    target_column_name : str
        The name of the column the deployed model uses for prediction output.
    deployment_id : str
        The ID of the deployment.
    model_id : str
        The ID of the underlying deployed model, which can be found using `Deployment.model["id"]`.
    validation_status : str
        Can be TESTING, FAILED, or PASSED. Only PASSED is allowed for use.
    deployment_access_data : dict, optional
        The data that will be used for accessing the deployment prediction server.
        This field is only available for deployments that pass validation.
        Dict fields are as follows:
        - prediction_api_url - The URL for the deployment prediction server.
        - datarobot_key - The first of two auth headers for the prediction server.
        - authorization_header - The second of two auth headers for the prediction server.
        - input_type - The input type the model expects, either JSON or CSV.
        - model_type - The target type of the deployed custom model.
    tenant_id : str
        The creating user's tenant ID.
    name : str
        The display name of the validated custom model.
    creation_date : str
        The creation date of the validation (ISO 8601 formatted).
    user_id : str
        The ID of the creating user.
    error_message : Optional[str]
        Additional information for the errored validation.
    deployment_name : Optional[str]
        The name of the validated deployment.
    user_name : Optional[str]
        The name of the creating user.
    use_case_id : Optional[str]
        The ID of the Use Case associated with the validation.
    prediction_timeout: int
        The timeout, in seconds, for the prediction API used in this custom model validation.
    """

    _path: str
    _converter = custom_model_validation_trafaret

    def __init__(
        self,
        id: str,
        prompt_column_name: str,
        target_column_name: str,
        deployment_id: str,
        model_id: str,
        validation_status: str,
        deployment_access_data: Optional[Dict[str, Any]],
        tenant_id: str,
        name: str,
        creation_date: str,
        user_id: str,
        error_message: Optional[str],
        deployment_name: Optional[str],
        user_name: Optional[str],
        use_case_id: Optional[str],
        prediction_timeout: int,
    ):
        self.id = id
        self.prompt_column_name = prompt_column_name
        self.target_column_name = target_column_name
        self.deployment_id = deployment_id
        self.model_id = model_id
        self.validation_status = validation_status
        self.deployment_access_data = deployment_access_data
        self.tenant_id = tenant_id
        self.error_message = error_message
        self.name = name
        self.creation_date = creation_date
        self.user_id = user_id
        self.deployment_name = deployment_name
        self.user_name = user_name
        self.use_case_id = use_case_id
        self.prediction_timeout = prediction_timeout

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    @classmethod
    def get(cls, validation_id: str) -> CustomModelValidation:
        """
        Get the validation record by id.

        Parameters
        ----------
        validation_id : Union[CustomModelValidation, str]
            The CustomModelValidation to retrieve, either `CustomModelValidation` or validation ID.

        Returns
        -------
        CustomModelValidation
        """
        url = f"{cls._client.domain}/{cls._path}/{get_entity_id(validation_id)}/"
        response = cls._client.get(url)
        return cls.from_server_data(response.json())

    @classmethod
    def get_by_values(
        cls, prompt_column_name: str, target_column_name: str, deployment_id: str, model_id: str
    ) -> CustomModelValidation:
        """
        Get the validation record by field values.

        Parameters
        ----------
        prompt_column_name : str
            The name of the column the deployed model uses for prompt text input.
        target_column_name : str
            The name of the column the deployed model uses for prediction output.
        deployment_id : str
            The ID of the deployment.
        model_id : str
            The ID of the underlying deployed model.

        Returns
        -------
        CustomModelValidation
        """

        url = f"{cls._client.domain}/{cls._path}/"
        params = {
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": deployment_id,
            "model_id": model_id,
            "order_by": "-creationDate",
            "limit": 1,
        }
        response_body = cls._client.get(url, params=params).json()
        data = response_body.get("data")

        if data is None:
            return cls.from_server_data(response_body)
        else:
            if len(data) == 0:
                raise ClientError(
                    exc_message="Custom model LLM validation not found", status_code=404
                )
            else:
                return cls.from_server_data(data[0])

    @classmethod
    def list(
        cls,
        prompt_column_name: Optional[str] = None,
        target_column_name: Optional[str] = None,
        deployment: Optional[Union[Deployment, str]] = None,
        model: Optional[Union[Model, str]] = None,
        use_cases: Optional[UseCaseLike] = None,
        playground: Optional[Union[Playground, str]] = None,
        completed_only: bool = False,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[CustomModelValidation]:
        """
        List the validation records by field values.

        Parameters
        ----------
        prompt_column_name : Optional[str], optional
            The column name the deployed model expects as the input.
        target_column_name : Optional[str], optional
            The target name that the deployed model will output.
        deployment : Optional[Union[Deployment, str]], optional
            The returned validations are filtered to those associated with a specific deployment
            if specified, either `Deployment` or the deployment ID.
        model_id : Optional[Union[Model, str]], optional
            The returned validations are filtered to those associated with a specific model
            if specified, either `Model` or model ID.
        use_cases : Optional[list[Union[UseCase, str]]], optional
            The returned validations are filtered to those associated with specific Use Cases
            if specified, either `UseCase` objects or the Use Case IDs.
        playground_id : Optional[Union[Playground, str]], optional
            The returned validations are filtered to those used in a specific playground
            if specified, either `Playground` or playground ID.
        completed_only : Optional[bool]
            Whether to retrieve only completed validations.
        search : Optional[str], optional
            String for filtering validations.
            Validations that contain the string in name will be returned.
        sort : Optional[str], optional
            Property to sort validations by.
            Prefix the attribute name with a dash to sort in descending order,
            e.g. sort='-name'.
            Currently supported options are listed in ListCustomModelValidationsSortQueryParams
            but the values can differ with different platform versions.
            By default, the sort parameter is None which will result in
            validations being returned in order of creation time descending.

        Returns
        -------
        List[CustomModelValidation]
        """

        url = f"{cls._client.domain}/{cls._path}/"
        params = {
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": get_entity_id(deployment) if deployment else None,
            "model_id": get_entity_id(model) if model else None,
            "playground_id": get_entity_id(playground) if playground else None,
            "completed_only": completed_only,
            "search": search,
            "sort": sort if sort else "-creationDate",
        }
        params = resolve_use_cases(use_cases=use_cases, params=params, use_case_key="use_case_id")
        r_data = unpaginate(url, params, cls._client)
        return [cls.from_server_data(data) for data in r_data]

    @classmethod
    def revalidate(cls, validation_id: str) -> CustomModelValidation:
        """
        Revalidate an unlinked custom model vector database or LLM.
        This method is helpful when a deployment used as vector database or LLM is accidentally
        replaced with another model that stopped complying with the response schema requirements.

        Replace the deployment's model with a complying model and call this method instead of
        creating a new custom model validation from scratch.

        Another application is if the API token used to create a validation record got revoked and
        no longer can be used to call the deployment.
        Calling `revalidate` will update the validation record with the token currently in use.

        Parameters
        ----------
        validation_id : str
            The ID of the CustomModelValidation for revalidation.

        Returns
        -------
        CustomModelValidation
        """
        url = f"{cls._client.domain}/{cls._path}/{validation_id}/revalidate/"
        response = cls._client.post(url)
        return cls.from_server_data(response.json())

    def delete(self) -> None:
        """
        Delete the custom model validation.
        """
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        self._client.delete(url)


class NonChatAwareCustomModelValidation(CustomModelValidation):
    """
    The validation record checking the ability of the deployment to serve as a custom model resource
    (either vector database or an embedding model), while not using the chat completions API for
    inference.

    Attributes
    ----------
    id : str
        The ID of the validation.
    prompt_column_name : str
        The name of the column the deployed model uses for prompt text input.
    target_column_name : str
        The name of the column the deployed model uses for prediction output.
    deployment_id : str
        The ID of the deployment.
    model_id : str
        The ID of the underlying deployed model, which can be found using `Deployment.model["id"]`.
    validation_status : str
        Can be TESTING, FAILED and PASSED. Only PASSED allowed for use.
    deployment_access_data : dict, optional
        The data that will be used for accessing the deployment prediction server.
        This field is only available for deployments that pass validation.
        Dict fields are as follows:
        - prediction_api_url - The URL for the deployment prediction server.
        - datarobot_key - The first of two auth headers for the prediction server.
        - authorization_header - The second of two auth headers for the prediction server.
        - input_type - The input type the model expects, either JSON or CSV.
        - model_type - The target type of the deployed custom model.
    tenant_id : str
        The creating user's tenant ID.
    name : str
        The display name of the validated custom model.
    creation_date : str
        The creation date of the validation (ISO 8601 formatted).
    user_id : str
        The ID of the creating user.
    error_message : Optional[str]
        Additional information for the errored validation.
    deployment_name : Optional[str]
        The name of the validated deployment.
    user_name : Optional[str]
        The name of the creating user.
    use_case_id : Optional[str]
        The ID of the Use Case associated with the validation.
    """

    @classmethod
    def create(
        cls,
        prompt_column_name: str,
        target_column_name: str,
        deployment_id: Union[Deployment, str],
        model: Optional[Union[Model, str]] = None,
        use_case: Optional[Union[UseCase, str]] = None,
        name: Optional[str] = None,
        wait_for_completion: bool = False,
        prediction_timeout: Optional[int] = None,
    ) -> NonChatAwareCustomModelValidation:
        """
        Start the validation of the deployment that will serve as a custom model resource
        (vector database, embedding model, etc.).

        Parameters
        ----------
        prompt_column_name : str
            The column name the deployed model expect as the input.
        target_column_name : str
            The target name that the deployed model will output.
        deployment_id : Union[Deployment, str]
            The deployment to validate, either `Deployment` or the deployment ID.
        model : Optional[Union[Model, str]], optional
            The specific model within the deployment, either `Model` or the model ID.
            If not specified, the underlying model ID will be automatically derived from the
            deployment information.
        use_case : Optional[Union[UseCase, str]], optional
            The Use Case to link the validation to, either `UseCase` or the Use Case ID.
        name : Optional[str], optional
            The name of the validation.
        wait_for_completion : bool
            If set to `True`, the code will wait for the validation job to complete before returning
            results. If the job does not finish in 10 minutes, this method call raises a timeout
            error.
            If set to `False`, the code does not wait for the job to complete. Instead,
            `CustomModelValidation.get` can be used to poll for the status of the job using
            the validation ID returned by the method.
        prediction_timeout : Optional[int], optional
            The timeout, in seconds, for the prediction API used in this custom model validation.

        Returns
        -------
        NonChatAwareCustomModelValidation
        """

        payload = {
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": get_entity_id(deployment_id),
            "model_id": get_entity_id(model) if model else None,
            "use_case_id": get_use_case_id(use_case, is_required=False),
            "name": name,
        }
        if prediction_timeout is not None:
            payload["prediction_timeout"] = prediction_timeout  # type: ignore[assignment]
        url = f"{cls._client.domain}/{cls._path}/"
        response = cls._client.post(url, data=payload)
        if wait_for_completion:
            location = wait_for_async_resolution(cls._client, response.headers["Location"])
            return cls.from_location(location)
        return cls.from_server_data(response.json())

    def update(
        self,
        name: Optional[str] = None,
        prompt_column_name: Optional[str] = None,
        target_column_name: Optional[str] = None,
        deployment: Optional[Union[Deployment, str]] = None,
        model: Optional[Union[Model, str]] = None,
        prediction_timeout: Optional[int] = None,
    ) -> NonChatAwareCustomModelValidation:
        """
        Update a custom model validation.

        Parameters
        ----------
        name : Optional[str], optional
            The new name of the custom model validation.
        prompt_column_name : Optional[str], optional
            The new name of the prompt column.
        target_column_name : Optional[str], optional
            The new name of the target column.
        deployment : Optional[Union[Deployment, str]], optional
            The new deployment to validate.
        model : Optional[Union[Model, str]], optional
            The new model within the deployment to validate.
        prediction_timeout : Optional[int], optional
            The new timeout, in seconds, for the prediction API used in this custom model validation.

        Returns
        -------
        NonChatAwareCustomModelValidation
        """
        payload = {
            "name": name,
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": get_entity_id(deployment) if deployment else None,
            "model_id": get_entity_id(model) if model else None,
            "prediction_timeout": prediction_timeout,
        }
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        response = self._client.patch(url, data=payload)
        return self.from_server_data(response.json())
