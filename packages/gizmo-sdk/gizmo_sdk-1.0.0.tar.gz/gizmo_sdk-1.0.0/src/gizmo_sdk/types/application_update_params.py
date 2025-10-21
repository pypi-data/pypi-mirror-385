# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .state import State
from .._utils import PropertyInfo
from .milestone import Milestone
from .loan_purpose import LoanPurpose

__all__ = ["ApplicationUpdateParams"]


class ApplicationUpdateParams(TypedDict, total=False):
    crm_id: Annotated[str, PropertyInfo(alias="crmId")]

    loan_purpose: Annotated[LoanPurpose, PropertyInfo(alias="loanPurpose")]

    los_id: Annotated[str, PropertyInfo(alias="losId")]

    primary_borrower_date_of_birth: Annotated[str, PropertyInfo(alias="primaryBorrowerDateOfBirth")]

    primary_borrower_email: Annotated[str, PropertyInfo(alias="primaryBorrowerEmail")]

    primary_borrower_first_name: Annotated[str, PropertyInfo(alias="primaryBorrowerFirstName")]

    primary_borrower_last_name: Annotated[str, PropertyInfo(alias="primaryBorrowerLastName")]

    primary_borrower_phone: Annotated[str, PropertyInfo(alias="primaryBorrowerPhone")]

    primary_borrower_ssn: Annotated[str, PropertyInfo(alias="primaryBorrowerSsn")]

    status: Milestone

    subject_property_city: Annotated[str, PropertyInfo(alias="subjectPropertyCity")]

    subject_property_state: Annotated[State, PropertyInfo(alias="subjectPropertyState")]
    """The two-letter state abbreviation in lowercase"""

    subject_property_street_address: Annotated[str, PropertyInfo(alias="subjectPropertyStreetAddress")]

    subject_property_zip: Annotated[str, PropertyInfo(alias="subjectPropertyZip")]
