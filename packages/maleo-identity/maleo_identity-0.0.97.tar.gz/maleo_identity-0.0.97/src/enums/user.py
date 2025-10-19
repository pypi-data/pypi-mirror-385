from enum import StrEnum
from maleo.types.string import ListOfStrs


class Granularity(StrEnum):
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    USERNAME = "username"
    EMAIL = "email"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class SchemaType(StrEnum):
    CORE = "core"
    COMPLETE = "complete"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]
