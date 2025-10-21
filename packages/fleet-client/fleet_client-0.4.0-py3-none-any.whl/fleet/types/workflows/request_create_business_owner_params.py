# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RequestCreateBusinessOwnerParams"]


class RequestCreateBusinessOwnerParams(TypedDict, total=False):
    company_url: Required[str]
    """The URL of the business to find the owner for"""

    n_pages: int
    """Number of pages to scrape for owner information"""
