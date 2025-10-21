import os
import re
import sys
from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import AnyHttpUrl, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from rallycli.models import RallyPydanticBase


class RallyTypeGeneric(RallyPydanticBase):
    ObjectID: Optional[Union[str, int]] = None
    VersionId: Optional[str] = None
    CreationDate: Optional[datetime] = None
    ref: Optional[Union[AnyHttpUrl, str]] = Field(
        default=None,
        alias="_ref",
    )
    refObjectName: Optional[str] = Field(
        default=None,
        alias="_refObjectName",
    )
    type: Optional[str] = Field(
        default=None,
        alias="_type",
    )
    objectVersion: Optional[str] = Field(
        default=None,
        alias="_objectVersion",
    )

    @staticmethod
    def get_oid_from_ref(ref: str) -> str:
        oid_from_ref = re.compile(r".*/(\d+)$")
        if match := oid_from_ref.match(ref):
            return match.group(1)
        return ""


class User(RallyTypeGeneric):
    ObjectUUID: Optional[str] = None
    AccountLockedUntil: Optional[datetime] = None
    ArtifactsCreated: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    ArtifactsOwned: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    CostCenter: Optional[str] = None
    DateFormat: Optional[str] = None
    DateTimeFormat: Optional[str] = None
    DefaultDetailPageToViewingMode: Optional[bool] = None
    DefaultProject: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Deleted: Optional[bool] = None
    Department: Optional[str] = None
    Disabled: Optional[bool] = None
    DisplayName: Optional[str] = None
    EmailAddress: Optional[str] = None
    EmailNotificationEnabled: Optional[Union[str, bool]] = None
    FirstName: Optional[str] = None
    InvestmentAdmin: Optional[bool] = None
    LandingPage: Optional[str] = None
    Language: Optional[str] = None
    LastActiveDate: Optional[str] = None
    LastLoginDate: Optional[datetime] = None
    LastName: Optional[str] = None
    LastPasswordUpdateDate: Optional[datetime] = None
    LastSystemTimeZoneName: Optional[str] = None
    Locale: Optional[str] = None
    MiddleName: Optional[str] = None
    NetworkID: Optional[str] = None
    OfficeLocation: Optional[str] = None
    OnpremLdapUsername: Optional[str] = None
    PasswordExpires: Optional[int] = None
    Phone: Optional[str] = None
    Planner: Optional[bool] = None
    ProfileImage: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    ProjectScopeDown: Optional[bool] = None
    ProjectScopeUp: Optional[bool] = None
    Role: Optional[str] = None
    sessionTimeout: Optional[int] = None
    SessionTimeoutWarning: Optional[bool] = None
    ShortDisplayName: Optional[str] = None
    SubscriptionAdmin: Optional[bool] = None
    Subscription: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    SubscriptionID: Optional[int] = None
    SubscriptionPermission: Optional[str] = None
    TeamMemberships: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    UserName: Optional[str] = None
    UserPermissions: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    UserProfile: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    WorkspacePermission: Optional[str] = None
    ZuulID: Optional[str] = None
    c_Empresa: Optional[str] = None
    c_Matricula: Optional[str] = None


class Project(RallyTypeGeneric):
    Name: Optional[str] = None


class ProjectPermission(RallyTypeGeneric):
    Role: Optional[Literal["Admin", "Editor", "Viewer"]] = None
    Name: Optional[str] = None
    User: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Project: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class Workspace(RallyTypeGeneric):
    Subscription: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class AllowedValue(RallyTypeGeneric):
    AttributeDefinition: Optional[Union[str, RallyTypeGeneric]] = None
    IntegerValue: Optional[int] = None
    LocalizedStringValue: Optional[str] = None
    StringValue: Optional[str] = None
    ValueIndex: Optional[int] = None


class Attdefinition(RallyTypeGeneric):
    Name: Optional[str] = None
    ElementName: Optional[str] = None
    AllowedValues: Optional[Union[str, RallyTypeGeneric]] = None
    AttributeType: Optional[str] = None
    RealAttributeType: Optional[str] = None
    Custom: Optional[bool] = None
    TypeDefinition: Optional[Union[str, RallyTypeGeneric]] = None
    ReadOnly: Optional[bool] = None
    Hidden: Optional[bool] = None
    Required: Optional[bool] = None


class Milestone(RallyTypeGeneric):
    FormattedID: Optional[str] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    Notes: Optional[str] = None
    Artifacts: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Projects: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TargetDate: Optional[datetime] = None
    TargetProject: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TotalArtifactCount: Optional[int] = None
    TotalProjectCount: Optional[int] = None
    c_Estado: Optional[str] = None
    c_ReferenciaExterna: Optional[str] = None


class Iteration(RallyTypeGeneric):
    FormattedID: Optional[str] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    StartDate: Optional[datetime] = None
    EndDate: Optional[datetime] = None
    State: Optional[str] = None
    Project: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    WorkProducts: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
