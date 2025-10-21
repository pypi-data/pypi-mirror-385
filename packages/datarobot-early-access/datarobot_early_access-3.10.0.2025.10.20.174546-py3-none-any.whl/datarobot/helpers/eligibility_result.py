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


class EligibilityResult:
    """Represents whether a particular operation is supported

    For instance, a function to check whether a set of models can be blended can return an
    EligibilityResult specifying whether or not blending is supported and why it may not be
    supported.

    Attributes
    ----------
    supported : bool
        whether the operation this result represents is supported
    reason : str
        why the operation is or is not supported
    context : str
        what operation isn't supported
    """

    def __init__(self, supported: bool, reason: str = "", context: str = "") -> None:
        self.supported = supported
        self.reason = reason
        self.context = context

    def __repr__(self) -> str:
        return "{}(supported={}, reason='{}', context='{}')".format(
            self.__class__.__name__, self.supported, self.reason, self.context
        )
