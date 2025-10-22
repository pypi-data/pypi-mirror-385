# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .mass import (
    MassResource,
    AsyncMassResource,
    MassResourceWithRawResponse,
    AsyncMassResourceWithRawResponse,
    MassResourceWithStreamingResponse,
    AsyncMassResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.workflows import WaitUntil, request_create_params, request_create_business_owner_params
from ....types.workflows.wait_until import WaitUntil
from ....types.workflows.request_create_response import RequestCreateResponse
from ....types.workflows.request.workflow_result_with_message import WorkflowResultWithMessage

__all__ = ["RequestResource", "AsyncRequestResource"]


class RequestResource(SyncAPIResource):
    @cached_property
    def mass(self) -> MassResource:
        return MassResource(self._client)

    @cached_property
    def with_raw_response(self) -> RequestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return RequestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RequestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return RequestResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        url: str,
        camo: bool | Omit = omit,
        ephemeral_browser: bool | Omit = omit,
        stealth: bool | Omit = omit,
        wait_until: WaitUntil | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestCreateResponse:
        """
        Make a request to temporal worker

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/workflows/request/scrape",
            body=maybe_transform(
                {
                    "url": url,
                    "camo": camo,
                    "ephemeral_browser": ephemeral_browser,
                    "stealth": stealth,
                    "wait_until": wait_until,
                },
                request_create_params.RequestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestCreateResponse,
        )

    def create_business_owner(
        self,
        *,
        company_name: str,
        addresses: Optional[SequenceNotStr[str]] | Omit = omit,
        camo: bool | Omit = omit,
        company_url: Optional[str] | Omit = omit,
        emails: Optional[SequenceNotStr[str]] | Omit = omit,
        max_steps: int | Omit = omit,
        n_google_links: int | Omit = omit,
        n_pages: int | Omit = omit,
        personnel_names: Optional[SequenceNotStr[str]] | Omit = omit,
        proxy_password: Optional[str] | Omit = omit,
        proxy_url: Optional[str] | Omit = omit,
        proxy_username: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkflowResultWithMessage:
        """
        Make a request to temporal worker

        Args:
          company_name: The name of the business

          addresses: Optional list of addresses associated with the business

          camo: Whether to use CAMO for scraping (if available)

          company_url: The URL of the business to find the owner for

          emails: Optional list of emails associated with the business

          max_steps: Maximum number of steps the agent can take

          n_google_links: Number of Google search links to consider if needed

          n_pages: Number of pages to scrape for owner information

          personnel_names: List of people associated with the business

          proxy_password: Optional proxy password

          proxy_url: Optional proxy URL to use for web requests

          proxy_username: Optional proxy username

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/workflows/request/business-owner",
            body=maybe_transform(
                {
                    "company_name": company_name,
                    "addresses": addresses,
                    "camo": camo,
                    "company_url": company_url,
                    "emails": emails,
                    "max_steps": max_steps,
                    "n_google_links": n_google_links,
                    "n_pages": n_pages,
                    "personnel_names": personnel_names,
                    "proxy_password": proxy_password,
                    "proxy_url": proxy_url,
                    "proxy_username": proxy_username,
                },
                request_create_business_owner_params.RequestCreateBusinessOwnerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowResultWithMessage,
        )


class AsyncRequestResource(AsyncAPIResource):
    @cached_property
    def mass(self) -> AsyncMassResource:
        return AsyncMassResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRequestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/fleet-client#accessing-raw-response-data-eg-headers
        """
        return AsyncRequestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRequestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/fleet-client#with_streaming_response
        """
        return AsyncRequestResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        url: str,
        camo: bool | Omit = omit,
        ephemeral_browser: bool | Omit = omit,
        stealth: bool | Omit = omit,
        wait_until: WaitUntil | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestCreateResponse:
        """
        Make a request to temporal worker

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/workflows/request/scrape",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "camo": camo,
                    "ephemeral_browser": ephemeral_browser,
                    "stealth": stealth,
                    "wait_until": wait_until,
                },
                request_create_params.RequestCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RequestCreateResponse,
        )

    async def create_business_owner(
        self,
        *,
        company_name: str,
        addresses: Optional[SequenceNotStr[str]] | Omit = omit,
        camo: bool | Omit = omit,
        company_url: Optional[str] | Omit = omit,
        emails: Optional[SequenceNotStr[str]] | Omit = omit,
        max_steps: int | Omit = omit,
        n_google_links: int | Omit = omit,
        n_pages: int | Omit = omit,
        personnel_names: Optional[SequenceNotStr[str]] | Omit = omit,
        proxy_password: Optional[str] | Omit = omit,
        proxy_url: Optional[str] | Omit = omit,
        proxy_username: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WorkflowResultWithMessage:
        """
        Make a request to temporal worker

        Args:
          company_name: The name of the business

          addresses: Optional list of addresses associated with the business

          camo: Whether to use CAMO for scraping (if available)

          company_url: The URL of the business to find the owner for

          emails: Optional list of emails associated with the business

          max_steps: Maximum number of steps the agent can take

          n_google_links: Number of Google search links to consider if needed

          n_pages: Number of pages to scrape for owner information

          personnel_names: List of people associated with the business

          proxy_password: Optional proxy password

          proxy_url: Optional proxy URL to use for web requests

          proxy_username: Optional proxy username

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/workflows/request/business-owner",
            body=await async_maybe_transform(
                {
                    "company_name": company_name,
                    "addresses": addresses,
                    "camo": camo,
                    "company_url": company_url,
                    "emails": emails,
                    "max_steps": max_steps,
                    "n_google_links": n_google_links,
                    "n_pages": n_pages,
                    "personnel_names": personnel_names,
                    "proxy_password": proxy_password,
                    "proxy_url": proxy_url,
                    "proxy_username": proxy_username,
                },
                request_create_business_owner_params.RequestCreateBusinessOwnerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowResultWithMessage,
        )


class RequestResourceWithRawResponse:
    def __init__(self, request: RequestResource) -> None:
        self._request = request

        self.create = to_raw_response_wrapper(
            request.create,
        )
        self.create_business_owner = to_raw_response_wrapper(
            request.create_business_owner,
        )

    @cached_property
    def mass(self) -> MassResourceWithRawResponse:
        return MassResourceWithRawResponse(self._request.mass)


class AsyncRequestResourceWithRawResponse:
    def __init__(self, request: AsyncRequestResource) -> None:
        self._request = request

        self.create = async_to_raw_response_wrapper(
            request.create,
        )
        self.create_business_owner = async_to_raw_response_wrapper(
            request.create_business_owner,
        )

    @cached_property
    def mass(self) -> AsyncMassResourceWithRawResponse:
        return AsyncMassResourceWithRawResponse(self._request.mass)


class RequestResourceWithStreamingResponse:
    def __init__(self, request: RequestResource) -> None:
        self._request = request

        self.create = to_streamed_response_wrapper(
            request.create,
        )
        self.create_business_owner = to_streamed_response_wrapper(
            request.create_business_owner,
        )

    @cached_property
    def mass(self) -> MassResourceWithStreamingResponse:
        return MassResourceWithStreamingResponse(self._request.mass)


class AsyncRequestResourceWithStreamingResponse:
    def __init__(self, request: AsyncRequestResource) -> None:
        self._request = request

        self.create = async_to_streamed_response_wrapper(
            request.create,
        )
        self.create_business_owner = async_to_streamed_response_wrapper(
            request.create_business_owner,
        )

    @cached_property
    def mass(self) -> AsyncMassResourceWithStreamingResponse:
        return AsyncMassResourceWithStreamingResponse(self._request.mass)
