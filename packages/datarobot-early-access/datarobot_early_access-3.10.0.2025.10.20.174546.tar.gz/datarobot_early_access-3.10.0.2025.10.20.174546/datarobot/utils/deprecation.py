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
"""This module is not considered part of the public interface. Anything here may change or
be removed without warning."""
from __future__ import annotations

import functools
from typing import Any, Callable, Optional
import warnings

from ..errors import DataRobotDeprecationWarning


def deprecation_warning(
    subject: str,
    deprecated_since_version: str,
    will_remove_version: Optional[str] = None,
    will_change_version: Optional[str] = None,
    message: Optional[str] = None,
) -> None:
    """
    Function that emits deprecation warning.

    Parameters
    ----------
    subject : str
        Deprecated subject
    deprecated_since_version : str
        The version of the SDK when this function was originally
        deprecated
    will_remove_version : str
        The _earliest_ version by which this function will be totally
        removed
    will_change_version: str
       The _earliest_ version by which this function will be changed in non compatible way
    message : Optional[str]
        Any specific information to add (i.e. preferred functions to
        use, etc.) If not specified, the warning will just indicate the
        function that was called, when it became deprecated and when
        it will be removed. Best practice is to make this message a full
        sentence, with correct capitalization and punctuation
    """
    if will_change_version:
        base_warn = "`{}` has been marked for change in `{}`, will be changed in `{}`"
        warn_msg = base_warn.format(subject, deprecated_since_version, will_change_version)
    elif will_remove_version:
        base_warn = "`{}` has been deprecated in `{}`, will be removed in `{}`"
        warn_msg = base_warn.format(subject, deprecated_since_version, will_remove_version)
    if message is not None:
        warn_msg = f"{warn_msg}. {message}"
    warnings.warn(warn_msg, DataRobotDeprecationWarning, stacklevel=3)


def deprecated(
    deprecated_since_version: str,
    will_change_version: Optional[str] = None,
    will_remove_version: Optional[str] = None,
    message: Optional[str] = None,
) -> Callable[..., Any]:
    """
    A decorator to mark functions as being deprecated

    Parameters
    ----------
    deprecated_since_version : str
        The version of the SDK when this function was originally
        deprecated
    will_remove_version : str
        The _earliest_ version by which this function will be totally
        removed
    will_change_version : str
        The _earliest_ version by which this function will be changed in backward incompatible way
    message : Optional[str]
        Any specific information to add (i.e. preferred functions to
        use, etc.) If not specified, the warning will just indicate the
        function that was called, when it became deprecated and when
        it will be removed. Best practice is to make this message a full
        sentence, with correct capitalization and punctuation.

    Returns
    -------
    func : callable
        The wrapped function
    """

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            deprecation_warning(
                func.__name__,
                deprecated_since_version,
                will_remove_version,
                will_change_version,
                message,
            )
            return func(*args, **kwargs)

        return inner

    return wrapper
