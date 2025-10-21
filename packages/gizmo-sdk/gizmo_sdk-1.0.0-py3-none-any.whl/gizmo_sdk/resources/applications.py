# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import State, Milestone, LoanPurpose, application_create_params, application_update_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.state import State
from .._base_client import make_request_options
from ..types.milestone import Milestone
from ..types.loan_purpose import LoanPurpose
from ..types.application_create_response import ApplicationCreateResponse
from ..types.application_update_response import ApplicationUpdateResponse
from ..types.application_retrieve_response import ApplicationRetrieveResponse

__all__ = ["ApplicationsResource", "AsyncApplicationsResource"]


class ApplicationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Gizmo-OS/gizmo-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Gizmo-OS/gizmo-sdk-python#with_streaming_response
        """
        return ApplicationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        lead_provider_slug: str,
        primary_borrower_email: str,
        primary_borrower_first_name: str,
        primary_borrower_last_name: str,
        primary_borrower_phone: str,
        subject_property_state: State,
        crm_id: str | Omit = omit,
        loan_purpose: LoanPurpose | Omit = omit,
        los_id: str | Omit = omit,
        primary_borrower_date_of_birth: str | Omit = omit,
        primary_borrower_ssn: str | Omit = omit,
        subject_property_city: str | Omit = omit,
        subject_property_street_address: str | Omit = omit,
        subject_property_zip: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateResponse:
        """
        Create Application

        Args:
          subject_property_state: The two-letter state abbreviation in lowercase

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/applications",
            body=maybe_transform(
                {
                    "lead_provider_slug": lead_provider_slug,
                    "primary_borrower_email": primary_borrower_email,
                    "primary_borrower_first_name": primary_borrower_first_name,
                    "primary_borrower_last_name": primary_borrower_last_name,
                    "primary_borrower_phone": primary_borrower_phone,
                    "subject_property_state": subject_property_state,
                    "crm_id": crm_id,
                    "loan_purpose": loan_purpose,
                    "los_id": los_id,
                    "primary_borrower_date_of_birth": primary_borrower_date_of_birth,
                    "primary_borrower_ssn": primary_borrower_ssn,
                    "subject_property_city": subject_property_city,
                    "subject_property_street_address": subject_property_street_address,
                    "subject_property_zip": subject_property_zip,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationRetrieveResponse:
        """
        Get Application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/applications/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        crm_id: str | Omit = omit,
        loan_purpose: LoanPurpose | Omit = omit,
        los_id: str | Omit = omit,
        primary_borrower_date_of_birth: str | Omit = omit,
        primary_borrower_email: str | Omit = omit,
        primary_borrower_first_name: str | Omit = omit,
        primary_borrower_last_name: str | Omit = omit,
        primary_borrower_phone: str | Omit = omit,
        primary_borrower_ssn: str | Omit = omit,
        status: Milestone | Omit = omit,
        subject_property_city: str | Omit = omit,
        subject_property_state: State | Omit = omit,
        subject_property_street_address: str | Omit = omit,
        subject_property_zip: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Optional[ApplicationUpdateResponse]:
        """
        Update Application

        Args:
          subject_property_state: The two-letter state abbreviation in lowercase

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/applications/{id}",
            body=maybe_transform(
                {
                    "crm_id": crm_id,
                    "loan_purpose": loan_purpose,
                    "los_id": los_id,
                    "primary_borrower_date_of_birth": primary_borrower_date_of_birth,
                    "primary_borrower_email": primary_borrower_email,
                    "primary_borrower_first_name": primary_borrower_first_name,
                    "primary_borrower_last_name": primary_borrower_last_name,
                    "primary_borrower_phone": primary_borrower_phone,
                    "primary_borrower_ssn": primary_borrower_ssn,
                    "status": status,
                    "subject_property_city": subject_property_city,
                    "subject_property_state": subject_property_state,
                    "subject_property_street_address": subject_property_street_address,
                    "subject_property_zip": subject_property_zip,
                },
                application_update_params.ApplicationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationUpdateResponse,
        )


class AsyncApplicationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Gizmo-OS/gizmo-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Gizmo-OS/gizmo-sdk-python#with_streaming_response
        """
        return AsyncApplicationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        lead_provider_slug: str,
        primary_borrower_email: str,
        primary_borrower_first_name: str,
        primary_borrower_last_name: str,
        primary_borrower_phone: str,
        subject_property_state: State,
        crm_id: str | Omit = omit,
        loan_purpose: LoanPurpose | Omit = omit,
        los_id: str | Omit = omit,
        primary_borrower_date_of_birth: str | Omit = omit,
        primary_borrower_ssn: str | Omit = omit,
        subject_property_city: str | Omit = omit,
        subject_property_street_address: str | Omit = omit,
        subject_property_zip: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationCreateResponse:
        """
        Create Application

        Args:
          subject_property_state: The two-letter state abbreviation in lowercase

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/applications",
            body=await async_maybe_transform(
                {
                    "lead_provider_slug": lead_provider_slug,
                    "primary_borrower_email": primary_borrower_email,
                    "primary_borrower_first_name": primary_borrower_first_name,
                    "primary_borrower_last_name": primary_borrower_last_name,
                    "primary_borrower_phone": primary_borrower_phone,
                    "subject_property_state": subject_property_state,
                    "crm_id": crm_id,
                    "loan_purpose": loan_purpose,
                    "los_id": los_id,
                    "primary_borrower_date_of_birth": primary_borrower_date_of_birth,
                    "primary_borrower_ssn": primary_borrower_ssn,
                    "subject_property_city": subject_property_city,
                    "subject_property_street_address": subject_property_street_address,
                    "subject_property_zip": subject_property_zip,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ApplicationRetrieveResponse:
        """
        Get Application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/applications/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        crm_id: str | Omit = omit,
        loan_purpose: LoanPurpose | Omit = omit,
        los_id: str | Omit = omit,
        primary_borrower_date_of_birth: str | Omit = omit,
        primary_borrower_email: str | Omit = omit,
        primary_borrower_first_name: str | Omit = omit,
        primary_borrower_last_name: str | Omit = omit,
        primary_borrower_phone: str | Omit = omit,
        primary_borrower_ssn: str | Omit = omit,
        status: Milestone | Omit = omit,
        subject_property_city: str | Omit = omit,
        subject_property_state: State | Omit = omit,
        subject_property_street_address: str | Omit = omit,
        subject_property_zip: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Optional[ApplicationUpdateResponse]:
        """
        Update Application

        Args:
          subject_property_state: The two-letter state abbreviation in lowercase

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/applications/{id}",
            body=await async_maybe_transform(
                {
                    "crm_id": crm_id,
                    "loan_purpose": loan_purpose,
                    "los_id": los_id,
                    "primary_borrower_date_of_birth": primary_borrower_date_of_birth,
                    "primary_borrower_email": primary_borrower_email,
                    "primary_borrower_first_name": primary_borrower_first_name,
                    "primary_borrower_last_name": primary_borrower_last_name,
                    "primary_borrower_phone": primary_borrower_phone,
                    "primary_borrower_ssn": primary_borrower_ssn,
                    "status": status,
                    "subject_property_city": subject_property_city,
                    "subject_property_state": subject_property_state,
                    "subject_property_street_address": subject_property_street_address,
                    "subject_property_zip": subject_property_zip,
                },
                application_update_params.ApplicationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationUpdateResponse,
        )


class ApplicationsResourceWithRawResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = to_raw_response_wrapper(
            applications.retrieve,
        )
        self.update = to_raw_response_wrapper(
            applications.update,
        )


class AsyncApplicationsResourceWithRawResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            applications.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            applications.update,
        )


class ApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            applications.update,
        )


class AsyncApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            applications.update,
        )
