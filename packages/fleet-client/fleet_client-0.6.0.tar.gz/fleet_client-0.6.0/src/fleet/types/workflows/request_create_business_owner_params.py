# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["RequestCreateBusinessOwnerParams"]


class RequestCreateBusinessOwnerParams(TypedDict, total=False):
    company_name: Required[str]
    """The name of the business"""

    addresses: Optional[SequenceNotStr[str]]
    """Optional list of addresses associated with the business"""

    camo: bool
    """Whether to use CAMO for scraping (if available)"""

    company_url: Optional[str]
    """The URL of the business to find the owner for"""

    emails: Optional[SequenceNotStr[str]]
    """Optional list of emails associated with the business"""

    max_steps: int
    """Maximum number of steps the agent can take"""

    n_google_links: int
    """Number of Google search links to consider if needed"""

    n_pages: int
    """Number of pages to scrape for owner information"""

    personnel_names: Optional[SequenceNotStr[str]]
    """List of people associated with the business"""

    proxy_password: Optional[str]
    """Optional proxy password"""

    proxy_url: Optional[str]
    """Optional proxy URL to use for web requests"""

    proxy_username: Optional[str]
    """Optional proxy username"""
