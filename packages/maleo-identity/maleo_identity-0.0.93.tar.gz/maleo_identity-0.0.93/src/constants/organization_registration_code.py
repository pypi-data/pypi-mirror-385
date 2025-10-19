from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import Resource, ResourceIdentifier
from ..enums.organization_registration_code import IdentifierType
from ..types.organization_registration_code import IdentifierValueType


IDENTIFIER_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.ORGANIZATION_ID: int,
    IdentifierType.CODE: UUID,
}


ORGANIZATION_REGISTRATION_CODE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_registration_codes",
            name="Organization Registration Codes",
            slug="organization-registration-codes",
        )
    ],
    details=None,
)
