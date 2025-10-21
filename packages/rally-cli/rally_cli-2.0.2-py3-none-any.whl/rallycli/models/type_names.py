"""Type literals for creating Rally WSAPI URL requests.
<https://eu1.rallydev.com/slm/webservice/v2.0/build>

Where "build" is the literal related to type_names.BUILD constant
"""

from enum import Enum

SCHEDULESTATE = {
    "New": "New",
    "Defined": "Defined",
    "In-Progress": "In-Progress",
    "Completed": "Completed",
    "Accepted": "Accepted",
}

US = "hierarchicalrequirement"
DEFECT = "defect"
TASK = "task"
TESTSET = "testset"
TESTCASE = "testcase"
TESTCASERESULT = "testcaseresult"
FEATURE = "portfolioitem/feature"
INITIATIVE = "portfolioitem/initiative"
TRACK = "portfolioitem/track"

USER = "user"
PROJECT = "project"
PROJECT_PERMISSION = "projectpermission"
RELEASE = "release"
ITERATION = "iteration"
MILESTONE = "milestone"
FLOWSTATE = "flowstate"
STATE = "state"
PULLREQUEST = "pullrequest"
BUILDDEFINITION = "builddefinition"
BUILD = "build"
SCMREPO = "scmrepository"
CHANGESET = "changeset"

TYPEDEF = "typedefinition"
ATTDEFINITION = "attributedefinition"
ALLOWEDVALUE = "allowedattributevalue"


class TestCaseResultVerdict(str, Enum):
    BLOCKED = "Blocked"
    ERROR = "Error"
    FAIL = "Fail"
    INCONCLUSIVE = "Inconclusive"
    PASS = "Pass"


class TestCaseStatus(str, Enum):
    NONE = "None"
    NONE_RUN = "None Run"
    SOME_RUN_NON_PASSING = "Some Run None Passing"
    SOME_RUN_SOME_NOT_PASSING = "Some Run Some Not Passing"
    SOME_RUN_ALL_PASSING = "Some Run All Passing"
    ALL_RUN_NONE_PASSING = "All Run None Passing"
    ALL_RUN_SOME_PASSING = "All Run Some Not Passing"
    ALL_RUN_ALL_PASSING = "All Run All Passing"


class DefectStatus(str, Enum):
    NONE2 = "NONE"
    NONE = "None"
    SOME_CLOSED = "Some Closed"
    NONE_CLOSED = "None Closed"
    ALL_CLOSED = "All Closed"


class TestCaseType(str, Enum):
    ACCEPTANCE = "Acceptance"
    ACCESIBILITY = "Accesibility"
    BUILD_VERIFICATION = "Build verification"
    FUNCTIONAL = "Functional"
    PERFORMANCE = "Performance"
    REGRESSION = "Regression"
    SMOKE = "Smoke"
    SYSTEM_INTEGRATION = "System Integration"
    UNCLASSIFIED = "Unclassified"
    USABILITY = "Usability"
    USER_INTERFACE = "User Interface"


class TestSetType(str, Enum):
    ACCEPTANCE = "Acceptance"
    END_TO_END = "End to End"
    EXPLORATORY = "Exploratory"
    REGRESSION = "Regression"
    SYSTEM_INTEGRATION = "System Integration"


class TestCaseMethod(str, Enum):
    MANUAL = "Manual"
    AUTOMATED = "Automated"
