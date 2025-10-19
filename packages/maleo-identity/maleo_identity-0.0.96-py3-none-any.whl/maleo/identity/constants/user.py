from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import Resource, ResourceIdentifier
from ..enums.user import IdentifierType
from ..types.user import IdentifierValueType


IDENTIFIER_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.EMAIL: str,
    IdentifierType.USERNAME: str,
}


USER_RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="users", name="Users", slug="users")],
    details=None,
)
