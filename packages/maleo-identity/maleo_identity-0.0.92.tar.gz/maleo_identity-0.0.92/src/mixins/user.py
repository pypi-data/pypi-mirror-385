from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.types.string import OptStrT, OptListOfStrsT


class Username(BaseModel, Generic[OptStrT]):
    username: Annotated[
        OptStrT, Field(..., description="User's username", max_length=50)
    ]


class Usernames(BaseModel, Generic[OptListOfStrsT]):
    usernames: Annotated[OptListOfStrsT, Field(..., description="User's Usernames")]


class Email(BaseModel, Generic[OptStrT]):
    email: Annotated[OptStrT, Field(..., description="User's email", max_length=255)]


class Emails(BaseModel, Generic[OptListOfStrsT]):
    emais: Annotated[OptListOfStrsT, Field(..., description="User's Emails")]


class Phone(BaseModel, Generic[OptStrT]):
    phone: Annotated[OptStrT, Field(..., description="User's phone", max_length=15)]


class Phones(BaseModel, Generic[OptListOfStrsT]):
    phones: Annotated[OptListOfStrsT, Field(..., description="User's Phones")]


class Password(BaseModel):
    password: Annotated[str, Field(..., description="Password", max_length=255)]
