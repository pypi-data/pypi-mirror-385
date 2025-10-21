# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .state import State
from .._utils import PropertyInfo
from .loan_purpose import LoanPurpose

__all__ = ["ApplicationCreateParams"]


class ApplicationCreateParams(TypedDict, total=False):
    lead_provider_slug: Required[Annotated[str, PropertyInfo(alias="leadProviderSlug")]]

    primary_borrower_email: Required[Annotated[str, PropertyInfo(alias="primaryBorrowerEmail")]]

    primary_borrower_first_name: Required[Annotated[str, PropertyInfo(alias="primaryBorrowerFirstName")]]

    primary_borrower_last_name: Required[Annotated[str, PropertyInfo(alias="primaryBorrowerLastName")]]

    primary_borrower_phone: Required[Annotated[str, PropertyInfo(alias="primaryBorrowerPhone")]]

    subject_property_state: Required[Annotated[State, PropertyInfo(alias="subjectPropertyState")]]
    """The two-letter state abbreviation in lowercase"""

    crm_id: Annotated[str, PropertyInfo(alias="crmId")]

    loan_purpose: Annotated[LoanPurpose, PropertyInfo(alias="loanPurpose")]

    los_id: Annotated[str, PropertyInfo(alias="losId")]

    primary_borrower_date_of_birth: Annotated[str, PropertyInfo(alias="primaryBorrowerDateOfBirth")]

    primary_borrower_ssn: Annotated[str, PropertyInfo(alias="primaryBorrowerSsn")]

    subject_property_city: Annotated[str, PropertyInfo(alias="subjectPropertyCity")]

    subject_property_street_address: Annotated[str, PropertyInfo(alias="subjectPropertyStreetAddress")]

    subject_property_zip: Annotated[str, PropertyInfo(alias="subjectPropertyZip")]
