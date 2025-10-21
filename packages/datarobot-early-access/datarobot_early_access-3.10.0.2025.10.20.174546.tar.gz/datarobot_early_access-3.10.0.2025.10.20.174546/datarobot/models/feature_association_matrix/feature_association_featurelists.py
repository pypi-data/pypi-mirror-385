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

from typing import TYPE_CHECKING, Dict, List, Optional

import trafaret as t

from datarobot._compat import String
from datarobot.models.api_object import APIObject

if TYPE_CHECKING:
    from datarobot._compat import TypedDict

    class FeatureListType(TypedDict):
        featurelist_id: str
        title: str
        has_fam: bool


class FeatureAssociationFeaturelists(APIObject):
    """
    Featurelists with feature association matrix availability flags for a project.

    Attributes
    ----------
    project_id : str
        Id of the project that contains the requested associations.
    featurelists : list fo dict
        The featurelists with the `featurelist_id`, `title` and the `has_fam` flag.
    """

    _path = "projects/{}/featureAssociationFeaturelists/"
    _converter = t.Dict(
        {
            t.Key("featurelists"): t.List(
                t.Dict(
                    {
                        t.Key("featurelist_id"): String(),
                        t.Key("title"): String(),
                        t.Key("has_fam"): t.Bool(),
                    }
                )
            )
        }
    )

    def __init__(
        self,
        project_id: Optional[str] = None,
        featurelists: Optional[List[FeatureListType]] = None,
    ) -> None:
        self.project_id = project_id
        self.featurelists = featurelists

    def __repr__(self) -> str:
        return "{}(project_id={}, featurelists={})".format(
            self.__class__.__name__, self.project_id, self.featurelists
        )

    @classmethod
    def get(cls, project_id: str) -> FeatureAssociationFeaturelists:
        """
        Get featurelists with feature association status for each.

        Parameters
        ----------
        project_id : str
             Id of the project of interest.

        Returns
        -------
        FeatureAssociationFeaturelists
            Featurelist with feature association status for each.
        """
        url = cls._path.format(project_id)
        response = cls._client.get(url)
        fam_featurelists = cls.from_server_data(response.json())
        fam_featurelists.project_id = project_id
        return fam_featurelists

    def to_dict(self) -> Dict[str, Optional[List[FeatureListType]]]:
        return {"featurelists": self.featurelists}
