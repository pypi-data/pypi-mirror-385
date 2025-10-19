# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["ProfileCaptureParams"]


class ProfileCaptureParams(TypedDict, total=False):
    url: Required[str]

    resource_types: Optional[SequenceNotStr[str]]
