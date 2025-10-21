# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Optional, cast

import pytest

from gizmo_sdk import Gizmo, AsyncGizmo
from tests.utils import assert_matches_type
from gizmo_sdk.types import (
    ApplicationCreateResponse,
    ApplicationUpdateResponse,
    ApplicationRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestApplications:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Gizmo) -> None:
        application = client.applications.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        )
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Gizmo) -> None:
        application = client.applications.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
            crm_id="crmId",
            loan_purpose="purchase",
            los_id="losId",
            primary_borrower_date_of_birth="primaryBorrowerDateOfBirth",
            primary_borrower_ssn="primaryBorrowerSsn",
            subject_property_city="subjectPropertyCity",
            subject_property_street_address="subjectPropertyStreetAddress",
            subject_property_zip="subjectPropertyZip",
        )
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Gizmo) -> None:
        response = client.applications.with_raw_response.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = response.parse()
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Gizmo) -> None:
        with client.applications.with_streaming_response.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = response.parse()
            assert_matches_type(ApplicationCreateResponse, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Gizmo) -> None:
        application = client.applications.retrieve(
            "id",
        )
        assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Gizmo) -> None:
        response = client.applications.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = response.parse()
        assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Gizmo) -> None:
        with client.applications.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = response.parse()
            assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Gizmo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.applications.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Gizmo) -> None:
        application = client.applications.update(
            id="id",
        )
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Gizmo) -> None:
        application = client.applications.update(
            id="id",
            crm_id="crmId",
            loan_purpose="purchase",
            los_id="losId",
            primary_borrower_date_of_birth="primaryBorrowerDateOfBirth",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            primary_borrower_ssn="primaryBorrowerSsn",
            status="NEW",
            subject_property_city="subjectPropertyCity",
            subject_property_state="al",
            subject_property_street_address="subjectPropertyStreetAddress",
            subject_property_zip="subjectPropertyZip",
        )
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Gizmo) -> None:
        response = client.applications.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = response.parse()
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Gizmo) -> None:
        with client.applications.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = response.parse()
            assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Gizmo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.applications.with_raw_response.update(
                id="",
            )


class TestAsyncApplications:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncGizmo) -> None:
        application = await async_client.applications.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        )
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGizmo) -> None:
        application = await async_client.applications.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
            crm_id="crmId",
            loan_purpose="purchase",
            los_id="losId",
            primary_borrower_date_of_birth="primaryBorrowerDateOfBirth",
            primary_borrower_ssn="primaryBorrowerSsn",
            subject_property_city="subjectPropertyCity",
            subject_property_street_address="subjectPropertyStreetAddress",
            subject_property_zip="subjectPropertyZip",
        )
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGizmo) -> None:
        response = await async_client.applications.with_raw_response.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = await response.parse()
        assert_matches_type(ApplicationCreateResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGizmo) -> None:
        async with async_client.applications.with_streaming_response.create(
            lead_provider_slug="leadProviderSlug",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            subject_property_state="al",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = await response.parse()
            assert_matches_type(ApplicationCreateResponse, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGizmo) -> None:
        application = await async_client.applications.retrieve(
            "id",
        )
        assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGizmo) -> None:
        response = await async_client.applications.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = await response.parse()
        assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGizmo) -> None:
        async with async_client.applications.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = await response.parse()
            assert_matches_type(ApplicationRetrieveResponse, application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGizmo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.applications.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncGizmo) -> None:
        application = await async_client.applications.update(
            id="id",
        )
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncGizmo) -> None:
        application = await async_client.applications.update(
            id="id",
            crm_id="crmId",
            loan_purpose="purchase",
            los_id="losId",
            primary_borrower_date_of_birth="primaryBorrowerDateOfBirth",
            primary_borrower_email="primaryBorrowerEmail",
            primary_borrower_first_name="primaryBorrowerFirstName",
            primary_borrower_last_name="primaryBorrowerLastName",
            primary_borrower_phone="primaryBorrowerPhone",
            primary_borrower_ssn="primaryBorrowerSsn",
            status="NEW",
            subject_property_city="subjectPropertyCity",
            subject_property_state="al",
            subject_property_street_address="subjectPropertyStreetAddress",
            subject_property_zip="subjectPropertyZip",
        )
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGizmo) -> None:
        response = await async_client.applications.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        application = await response.parse()
        assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGizmo) -> None:
        async with async_client.applications.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            application = await response.parse()
            assert_matches_type(Optional[ApplicationUpdateResponse], application, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncGizmo) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.applications.with_raw_response.update(
                id="",
            )
