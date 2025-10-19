from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import Resource, ResourceIdentifier
from ..enums.user_profile import IdentifierType
from ..types.user_profile import IdentifierValueType


IDENTIFIER_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
    IdentifierType.USER_ID: int,
    IdentifierType.ID_CARD: str,
}


USER_PROFILE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_profiles", name="User Profiles", slug="user-profiles"
        )
    ],
    details=None,
)
