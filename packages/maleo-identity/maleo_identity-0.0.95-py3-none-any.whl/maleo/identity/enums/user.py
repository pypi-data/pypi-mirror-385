from enum import StrEnum
from maleo.types.string import ListOfStrs


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    USERNAME = "username"
    EMAIL = "email"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]
