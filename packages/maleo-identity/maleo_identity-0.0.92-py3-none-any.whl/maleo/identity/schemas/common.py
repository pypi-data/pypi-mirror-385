from pydantic import BaseModel, Field
from typing import Annotated, Generic, TypeVar
from maleo.enums.identity import OptBloodType, BloodTypeMixin, OptGender, GenderMixin
from maleo.enums.medical import MedicalRole, FullMedicalRoleMixin
from maleo.enums.organization import (
    OrganizationRole,
    FullOrganizationRoleMixin,
    OrganizationType,
    FullOrganizationTypeMixin,
)
from maleo.enums.status import DataStatus as DataStatusEnum, SimpleDataStatusMixin
from maleo.enums.system import SystemRole, FullSystemRoleMixin
from maleo.enums.user import UserType, FullUserTypeMixin
from maleo.schemas.mixins.identity import DataIdentifier, IntOrganizationId, IntUserId
from maleo.schemas.mixins.timestamp import DataTimestamp
from maleo.types.datetime import OptDate
from maleo.types.string import OptStr
from ..mixins.organization_registration_code import Code, MaxUses, CurrentUses
from ..mixins.organization import Key as OrganizationKey, Name as OrganizationName
from ..mixins.user_profile import (
    IdCard,
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    FullName,
    BirthPlace,
    BirthDate,
    AvatarName,
)
from ..mixins.user import Username, Email, Phone


class OrganizationRegistrationCodeSchema(
    CurrentUses,
    MaxUses[int],
    Code[str],
    IntOrganizationId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


OptOrganizationRegistrationCodeSchema = OrganizationRegistrationCodeSchema | None


class OrganizationRegistrationCodeSchemaMixin(BaseModel):
    registration_code: Annotated[
        OptOrganizationRegistrationCodeSchema,
        Field(None, description="Organization's registration code"),
    ] = None


class StandardOrganizationCoreSchema(
    OrganizationName[str],
    OrganizationKey[str],
    FullOrganizationTypeMixin[OrganizationType],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class FullOrganizationCoreSchema(
    OrganizationRegistrationCodeSchemaMixin,
    StandardOrganizationCoreSchema,
):
    pass


AnyOrganizationCoreSchema = StandardOrganizationCoreSchema | FullOrganizationCoreSchema
AnyOrganizationCoreSchemaT = TypeVar(
    "AnyOrganizationCoreSchemaT", bound=AnyOrganizationCoreSchema
)


class OrganizationCoreSchemaMixin(BaseModel, Generic[AnyOrganizationCoreSchemaT]):
    organization: Annotated[
        AnyOrganizationCoreSchemaT, Field(..., description="Organization")
    ]


class UserMedicalRoleSchema(
    FullMedicalRoleMixin[MedicalRole],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserMedicalRolesSchemaMixin(BaseModel):
    medical_roles: Annotated[
        list[UserMedicalRoleSchema],
        Field(list[UserMedicalRoleSchema](), description="Medical roles"),
    ] = list[UserMedicalRoleSchema]()


class UserOrganizationRoleSchema(
    FullOrganizationRoleMixin[OrganizationRole],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationRolesSchemaMixin(BaseModel):
    organization_roles: Annotated[
        list[UserOrganizationRoleSchema],
        Field(list[UserOrganizationRoleSchema](), description="Organization roles"),
    ] = list[UserOrganizationRoleSchema]()


class UserProfileCoreSchema(
    AvatarName[str],
    BloodTypeMixin[OptBloodType],
    GenderMixin[OptGender],
    BirthDate[OptDate],
    BirthPlace[OptStr],
    FullName[str],
    EndingTitle[OptStr],
    LastName[str],
    MiddleName[OptStr],
    FirstName[str],
    LeadingTitle[OptStr],
    IdCard[OptStr],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


OptUserProfileCoreSchema = UserProfileCoreSchema | None


class UserProfileCoreSchemaMixin(BaseModel):
    profile: Annotated[
        OptUserProfileCoreSchema, Field(None, description="User's Profile")
    ] = None


class UserSystemRoleCoreSchema(
    FullSystemRoleMixin[SystemRole],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserSystemRolesCoreSchemaMixin(BaseModel):
    system_roles: Annotated[
        list[UserSystemRoleCoreSchema],
        Field(
            list[UserSystemRoleCoreSchema](),
            description="User's system roles",
            min_length=1,
        ),
    ] = list[UserSystemRoleCoreSchema]()


class StandardUserCoreSchema(
    UserProfileCoreSchemaMixin,
    Phone[str],
    Email[str],
    Username[str],
    FullUserTypeMixin[UserType],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class FullUserCoreSchema(UserSystemRolesCoreSchemaMixin, StandardUserCoreSchema):
    pass


AnyUserCoreSchema = StandardUserCoreSchema | FullUserCoreSchema
AnyUserCoreSchemaT = TypeVar("AnyUserCoreSchemaT", bound=AnyUserCoreSchema)


class UserCoreSchemaMixin(BaseModel, Generic[AnyUserCoreSchemaT]):
    user: Annotated[AnyUserCoreSchemaT, Field(..., description="User")]


class UserAndOrganizationSchema(
    UserMedicalRolesSchemaMixin,
    UserOrganizationRolesSchemaMixin,
):
    pass


class UserOrganizationSchema(
    UserAndOrganizationSchema,
    OrganizationCoreSchemaMixin[StandardOrganizationCoreSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationsSchemaMixin(BaseModel):
    organizations: Annotated[
        list[UserOrganizationSchema],
        Field(list[UserOrganizationSchema](), description="Organizations"),
    ] = list[UserOrganizationSchema]()


class StandardUserCompleteSchema(UserOrganizationsSchemaMixin, StandardUserCoreSchema):
    pass


class FullUserCompleteSchema(UserOrganizationsSchemaMixin, FullUserCoreSchema):
    pass


class OrganizationUserSchema(
    UserAndOrganizationSchema,
    UserCoreSchemaMixin[StandardUserCoreSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    DataTimestamp,
    DataIdentifier,
):
    pass


class OrganizationUsersSchemaMixin(BaseModel):
    users: Annotated[
        list[OrganizationUserSchema],
        Field(list[OrganizationUserSchema](), description="Users"),
    ] = list[OrganizationUserSchema]()


class StandardOrganizationCompleteSchema(
    OrganizationUsersSchemaMixin, StandardOrganizationCoreSchema
):
    pass


class FullOrganizationCompleteSchema(
    OrganizationUsersSchemaMixin, FullOrganizationCoreSchema
):
    pass
