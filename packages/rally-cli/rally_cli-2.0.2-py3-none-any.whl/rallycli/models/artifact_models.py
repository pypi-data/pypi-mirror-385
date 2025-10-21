from datetime import datetime
from typing import Any, Optional, Union

from pydantic import AnyHttpUrl, HttpUrl

from rallycli.models import RallyTypeGeneric, User
from rallycli.models.type_names import (
    DefectStatus,
    TestCaseMethod,
    TestCaseResultVerdict,
    TestCaseStatus,
    TestCaseType,
    TestSetType,
)


class Artifact(RallyTypeGeneric):
    Subscription: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Workspace: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    CreatedBy: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Description: Optional[str] = None
    Discussion: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    DisplayColor: Optional[str] = None
    FormattedID: Optional[str] = None
    LastUpdateDate: Optional[datetime] = None
    Milestones: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Name: Optional[str] = None
    Notes: Optional[str] = None
    Owner: Optional[Union[User, AnyHttpUrl, str]] = None
    Project: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Tags: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Blocked: Optional[bool] = None
    BlockedReason: Optional[str] = None
    Blocker: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    DirectChildrenCount: Optional[int] = None
    Parent: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Release: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class PortfolioItem(Artifact):
    State: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class Feature(PortfolioItem):
    UserStories: Optional[Union[RallyTypeGeneric, HttpUrl]] = None  # Modificable collection


class SchedulabeArtifact(Artifact):
    AcceptedDate: Optional[datetime] = None
    ScheduleState: Optional[str] = None
    Release: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Iteration: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    FlowState: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    FlowStateChangedDate: Optional[datetime] = None
    TaskActualTotal: Optional[float] = None
    TaskEstimateTotal: Optional[float] = None
    TaskRemainingTotal: Optional[float] = None
    TaskStatus: Optional[str] = None
    Tasks: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestCaseCount: Optional[int] = None
    ScheduleStatePrefix: Optional[str] = None
    PassingTestCaseCount: Optional[int] = None
    LastBuild: Optional[str] = None
    LastRun: Optional[datetime] = None


class US(SchedulabeArtifact):
    Expedite: Optional[bool] = None
    Ready: Optional[bool] = None
    Children: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    DefectStatus: Optional[str] = None
    Defects: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    HasParent: Optional[bool] = None
    InProgressDate: Optional[datetime] = None
    Recycled: Optional[bool] = None
    TestCaseStatus: Optional[str] = None
    TestCases: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Feature: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    PortfolioItem: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    c_Tipo: Optional[str] = None  # Custom field, type not specified
    c_ReferenciaExterna: Optional[str] = None  # Custom field, type not specified


class Defect(SchedulabeArtifact):
    AffectsDoc: Optional[bool] = None
    Attachments: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    ClosedDate: Optional[datetime] = None
    DefectSuites: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Duplicates: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Environment: Optional[str] = None
    FixedInBuild: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    FoundInBuild: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    InProgressDate: Optional[datetime] = None
    OpenedDate: Optional[datetime] = None
    PlanEstimate: Optional[Any] = None
    Priority: Optional[str] = None
    Recycled: Optional[bool] = None
    Requirement: Optional[Any] = None
    Resolution: Optional[str] = None
    Severity: Optional[str] = None
    SubmittedBy: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TargetBuild: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TargetDate: Optional[datetime] = None
    TestCase: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestCaseResult: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestCaseStatus: Optional[str] = None
    TestCases: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    VerifiedInBuild: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class Task(Artifact):
    WorkProduct: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    State: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class TestCase(Artifact):
    DefectStatus: Optional[Union[DefectStatus, str]] = DefectStatus.NONE
    Defects: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    LastBuild: Optional[str] = None
    LastResult: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    LastRun: Optional[datetime] = None
    LastVerdict: Optional[TestCaseResultVerdict] = None
    Method: Optional[TestCaseMethod] = None
    Objetive: Optional[str] = None
    Results: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Steps: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestFolder: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestSets: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Type: Optional[TestCaseType] = None  # * Enum
    WorkProduct: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    c_APPGAR: Optional[str] = None
    c_ComponentGAR: Optional[str] = None
    c_Canal: Optional[str] = None
    Priority: Optional[str] = None
    Objective: Optional[str] = None
    PreConditions: Optional[str] = None


class TestCaseResult(RallyTypeGeneric):
    FormattedID: Optional[str] = None
    TestCase: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    TestSet: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Tester: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    Verdict: Optional[TestCaseResultVerdict] = (
        None  # * Enum "Blocked", "Error", "Fail", "Inconclusive", "Pass"
    )
    Build: Optional[str] = None
    Date: Optional[datetime] = None
    Duration: Optional[float] = None
    Notes: Optional[str] = None
    Project: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    WorkProduct: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None


class TestSet(Artifact):
    DefectStatus: Optional[Union[DefectStatus, str]] = None
    Iteration: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    LastBuild: Optional[str] = None
    LastRun: Optional[datetime] = None
    PassingTestCaseCount: Optional[int] = None
    TestCaseCount: Optional[int] = None
    TestCaseStatus: Optional[Union[TestCaseStatus, str]] = None
    TestCases: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    c_APPGAR: Optional[str] = None
    c_Type: Optional[TestSetType] = None
    c_WorkProduct: Optional[Union[RallyTypeGeneric, AnyHttpUrl, str]] = None
    c_Environment: Optional[str] = None
