from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import Resource, ResourceIdentifier
from ..enums.organization import IdentifierType
from ..types.organization import IdentifierValueType


IDENTIFIER_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.KEY: str,
}


ORGANIZATION_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organizations", name="Organizations", slug="organizations"
        )
    ],
    details=None,
)
