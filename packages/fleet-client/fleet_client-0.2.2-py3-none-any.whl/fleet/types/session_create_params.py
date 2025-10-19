# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SessionCreateParams", "BrowserConfiguration"]


class SessionCreateParams(TypedDict, total=False):
    browser_configuration: Required[BrowserConfiguration]
    """Browser configuration."""

    agentic: bool

    enable_xvfb: bool

    n_responses_to_track: int

    proxy_password: str

    proxy_url: str

    proxy_username: str

    vnc_password: str


class BrowserConfiguration(TypedDict, total=False):
    camo: bool

    headless: bool

    stealth: bool

    track_all_responses: bool

    wait_until: str
