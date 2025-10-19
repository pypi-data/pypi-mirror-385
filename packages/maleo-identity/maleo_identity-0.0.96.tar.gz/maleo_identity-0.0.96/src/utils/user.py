from typing import Literal, Type, overload
from ..schemas.common import (
    StandardUserCoreSchema,
    FullUserCoreSchema,
    StandardUserCompleteSchema,
    FullUserCompleteSchema,
    AnyUserSchemaType,
)
from ..enums.user import Granularity, SchemaType


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    schema_type: Literal[SchemaType.CORE],
    /,
) -> Type[StandardUserCoreSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    schema_type: Literal[SchemaType.COMPLETE],
    /,
) -> Type[StandardUserCompleteSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    schema_type: Literal[SchemaType.CORE],
    /,
) -> Type[FullUserCoreSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    schema_type: Literal[SchemaType.COMPLETE],
    /,
) -> Type[FullUserCompleteSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    schema_type: SchemaType = SchemaType.CORE,
    /,
) -> AnyUserSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    schema_type: SchemaType = SchemaType.CORE,
    /,
) -> AnyUserSchemaType:
    if granularity is Granularity.STANDARD:
        if schema_type is SchemaType.CORE:
            return StandardUserCoreSchema
        elif schema_type is SchemaType.COMPLETE:
            return StandardUserCompleteSchema
    elif granularity is Granularity.FULL:
        if schema_type is SchemaType.CORE:
            return FullUserCoreSchema
        elif schema_type is SchemaType.COMPLETE:
            return FullUserCompleteSchema
