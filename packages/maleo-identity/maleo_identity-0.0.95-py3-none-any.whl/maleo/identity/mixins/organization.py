from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.schemas.mixins.identity import Key as BaseKey, Name as BaseName
from maleo.types.string import OptStrT
from maleo.types.uuid import OptUUIDT


class Key(BaseKey, Generic[OptStrT]):
    key: Annotated[OptStrT, Field(..., description="Key", max_length=255)]


class Name(BaseName, Generic[OptStrT]):
    name: Annotated[OptStrT, Field(..., description="Name", max_length=255)]


class Secret(BaseModel, Generic[OptUUIDT]):
    secret: Annotated[OptUUIDT, Field(..., description="Secret")]
