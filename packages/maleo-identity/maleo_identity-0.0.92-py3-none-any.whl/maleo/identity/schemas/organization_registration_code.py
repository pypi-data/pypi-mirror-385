from pydantic import BaseModel, Field
from typing import Generic, Literal, TypeVar, overload
from uuid import UUID
from maleo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.filter import convert as convert_filter
from maleo.schemas.mixins.general import Codes
from maleo.schemas.mixins.identity import (
    IdentifierTypeValue,
    Ids,
    IntOrganizationId,
    UUIDs,
    UUIDOrganizationIds,
)
from maleo.schemas.mixins.sort import convert as convert_sort
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.dict import StrToAnyDict
from maleo.types.integer import OptInt, OptListOfInts
from maleo.types.string import OptStr, OptListOfStrs
from maleo.types.uuid import OptListOfUUIDs
from ..enums.organization_registration_code import IdentifierType
from ..mixins.organization_registration_code import Code, MaxUses
from ..types.organization_registration_code import IdentifierValueType


class BaseCreateParameter(
    MaxUses[int],
    Code[OptStr],
):
    pass


class CreateParameter(
    BaseCreateParameter,
    IntOrganizationId[int],
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    Codes[OptListOfStrs],
    UUIDOrganizationIds[OptListOfUUIDs],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "organization_ids",
            "codes",
            "search",
            "page",
            "limit",
            "use_cache",
        }

    def to_query_params(self) -> StrToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


class ReadSingleParameter(BaseReadSingleParameter[IdentifierType, IdentifierValueType]):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID, IdentifierType.ORGANIZATION_ID],
        identifier_value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.CODE],
        identifier_value: str,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            statuses=statuses,
            use_cache=use_cache,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache"}, exclude_none=True
        )


class FullUpdateData(MaxUses[int], Code[str]):
    pass


class PartialUpdateData(MaxUses[OptInt], Code[OptStr]):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    UpdateDataMixin[UpdateDataT],
    IdentifierTypeValue[
        IdentifierType,
        IdentifierValueType,
    ],
    Generic[UpdateDataT],
):
    pass


class StatusUpdateParameter(
    BaseStatusUpdateParameter[IdentifierType, IdentifierValueType],
):
    pass


class DeleteSingleParameter(
    BaseDeleteSingleParameter[IdentifierType, IdentifierValueType]
):
    pass
