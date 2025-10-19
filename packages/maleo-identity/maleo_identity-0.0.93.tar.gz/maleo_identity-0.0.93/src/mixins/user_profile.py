from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.types.datetime import OptDateT
from maleo.types.string import OptStrT


class IdCard(BaseModel, Generic[OptStrT]):
    id_card: Annotated[OptStrT, Field(..., description="User's Id Card", max_length=16)]


class LeadingTitle(BaseModel, Generic[OptStrT]):
    leading_title: Annotated[
        OptStrT, Field(..., description="User's Leading Title", max_length=25)
    ]


class FirstName(BaseModel, Generic[OptStrT]):
    first_name: Annotated[
        OptStrT, Field(..., description="User's First Name", max_length=50)
    ]


class MiddleName(BaseModel, Generic[OptStrT]):
    middle_name: Annotated[
        OptStrT, Field(..., description="User's Middle Name", max_length=50)
    ]


class LastName(BaseModel, Generic[OptStrT]):
    last_name: Annotated[
        OptStrT, Field(..., description="User's Last Name", max_length=50)
    ]


class EndingTitle(BaseModel, Generic[OptStrT]):
    ending_title: Annotated[
        OptStrT, Field(..., description="User's Ending Title", max_length=25)
    ]


class FullName(BaseModel, Generic[OptStrT]):
    full_name: Annotated[
        OptStrT, Field(..., description="User's Full Name", max_length=200)
    ]


class BirthPlace(BaseModel, Generic[OptStrT]):
    birth_place: Annotated[
        OptStrT, Field(..., description="User's Birth Place", max_length=50)
    ]


class BirthDate(BaseModel, Generic[OptDateT]):
    birth_date: Annotated[OptDateT, Field(..., description="User's birth date")]


class AvatarName(BaseModel, Generic[OptStrT]):
    avatar_name: Annotated[OptStrT, Field(..., description="User's Avatar Name")]
