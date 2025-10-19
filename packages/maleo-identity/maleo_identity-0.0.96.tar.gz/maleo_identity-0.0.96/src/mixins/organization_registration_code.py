from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.types.integer import OptIntT
from maleo.types.string import OptStrT


class Code(BaseModel, Generic[OptStrT]):
    code: Annotated[OptStrT, Field(..., description="Code", max_length=36)]


class MaxUses(BaseModel, Generic[OptIntT]):
    max_uses: Annotated[OptIntT, Field(..., description="Max Uses", ge=1)]


class CurrentUses(BaseModel):
    current_uses: Annotated[int, Field(0, description="Current Uses", ge=0)] = 0
