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

from typing import Any, List, cast

import numpy
import trafaret as t

from datarobot.insights.base import CsvSupportedInsight


class ShapMatrix(CsvSupportedInsight):
    """Class for SHAP Matrix calculations. Use the standard methods of BaseInsight to compute
    and retrieve: compute, create, list, get.
    """

    INSIGHT_NAME = "shapMatrix"
    INSIGHT_DATA = {
        t.Key("index"): t.List(t.Int()),
        t.Key("link_function"): t.String(),
        t.Key("base_value"): t.Float(),
        t.Key("colnames"): t.List(t.String()),
        t.Key("matrix"): t.List(t.List(t.Or(t.Int(), t.Float()))),
    }

    @property
    def matrix(self) -> Any:  # numpy.types.NDArray is not compatible with sphinx docs.
        """SHAP matrix values."""
        return numpy.array(self.data["matrix"])

    @property
    def base_value(self) -> float:
        """SHAP base value for the matrix values"""
        return cast(float, self.data["base_value"])

    @property
    def columns(self) -> List[str]:
        """List of columns associated with the SHAP matrix"""
        return cast(List[str], self.data["colnames"])

    @property
    def link_function(self) -> str:
        """Link function used to generate the SHAP matrix"""
        return cast(str, self.data["link_function"])
