# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["TagRemoveParams"]


class TagRemoveParams(TypedDict, total=False):
    limit_tags: Required[SequenceNotStr[str]]
    """List of limit tags"""
