# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .state import State
from .._models import BaseModel
from .milestone import Milestone
from .loan_purpose import LoanPurpose

__all__ = ["ApplicationRetrieveResponse"]


class ApplicationRetrieveResponse(BaseModel):
    id: str

    created_at: float = FieldInfo(alias="createdAt")

    lead_provider_slug: str = FieldInfo(alias="leadProviderSlug")

    org_id: str = FieldInfo(alias="orgId")

    primary_borrower_email: str = FieldInfo(alias="primaryBorrowerEmail")

    primary_borrower_first_name: str = FieldInfo(alias="primaryBorrowerFirstName")

    primary_borrower_last_name: str = FieldInfo(alias="primaryBorrowerLastName")

    primary_borrower_phone: str = FieldInfo(alias="primaryBorrowerPhone")

    status: Milestone

    subject_property_state: State = FieldInfo(alias="subjectPropertyState")
    """The two-letter state abbreviation in lowercase"""

    crm_id: Optional[str] = FieldInfo(alias="crmId", default=None)

    loan_purpose: Optional[LoanPurpose] = FieldInfo(alias="loanPurpose", default=None)

    los_id: Optional[str] = FieldInfo(alias="losId", default=None)

    primary_borrower_date_of_birth: Optional[str] = FieldInfo(alias="primaryBorrowerDateOfBirth", default=None)

    primary_borrower_ssn: Optional[str] = FieldInfo(alias="primaryBorrowerSsn", default=None)

    subject_property_city: Optional[str] = FieldInfo(alias="subjectPropertyCity", default=None)

    subject_property_street_address: Optional[str] = FieldInfo(alias="subjectPropertyStreetAddress", default=None)

    subject_property_zip: Optional[str] = FieldInfo(alias="subjectPropertyZip", default=None)

    updated_at: Optional[float] = FieldInfo(alias="updatedAt", default=None)
