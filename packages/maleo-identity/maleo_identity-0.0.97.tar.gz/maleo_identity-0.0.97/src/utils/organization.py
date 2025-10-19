from typing import Literal, Type, overload
from ..schemas.common import (
    StandardOrganizationCoreSchema,
    FullOrganizationCoreSchema,
    StandardOrganizationCompleteSchema,
    FullOrganizationCompleteSchema,
    AnyOrganizationSchemaType,
)
from ..enums.organization import Granularity, SchemaType


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    schema_type: Literal[SchemaType.CORE],
    /,
) -> Type[StandardOrganizationCoreSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    schema_type: Literal[SchemaType.COMPLETE],
    /,
) -> Type[StandardOrganizationCompleteSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    schema_type: Literal[SchemaType.CORE],
    /,
) -> Type[FullOrganizationCoreSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    schema_type: Literal[SchemaType.COMPLETE],
    /,
) -> Type[FullOrganizationCompleteSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    schema_type: SchemaType = SchemaType.CORE,
    /,
) -> AnyOrganizationSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    schema_type: SchemaType = SchemaType.CORE,
    /,
) -> AnyOrganizationSchemaType:
    if granularity is Granularity.STANDARD:
        if schema_type is SchemaType.CORE:
            return StandardOrganizationCoreSchema
        elif schema_type is SchemaType.COMPLETE:
            return StandardOrganizationCompleteSchema
    elif granularity is Granularity.FULL:
        if schema_type is SchemaType.CORE:
            return FullOrganizationCoreSchema
        elif schema_type is SchemaType.COMPLETE:
            return FullOrganizationCompleteSchema
