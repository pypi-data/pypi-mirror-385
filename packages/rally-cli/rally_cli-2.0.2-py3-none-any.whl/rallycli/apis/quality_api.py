import os
import sys
from logging import getLogger

import urllib3

from rallycli.apis import ArtifactAPI
from rallycli.models import type_names
from rallycli.models.artifact_models import TestCase, TestCaseResult, TestSet

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


# logger definition
logger = getLogger(__name__)

# Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class QualityAPI(ArtifactAPI):
    """Class for accessing Time Boxes domain"""

    def get_testset_by_ref(self, testset_ref: str) -> TestSet:
        abs_ref = self._get_absolute_url_from_ref(testset_ref)
        return self.get_element_by_ref(abs_ref, model_class=TestSet)

    def create_testset(self, testset: TestSet) -> TestSet:
        return self.create_artifact(testset, type_names.TESTSET)

    def create_testcase(self, testcase: TestCase) -> TestCase:
        return self.create_artifact(testcase, type_names.TESTCASE)

    def create_testcaseresult(self, testcaseresult: TestCaseResult) -> TestCaseResult:
        result_object: dict = self._create_from_dump(
            testcaseresult.dump_for_create(), rally_type=type_names.TESTCASERESULT
        )
        obj = self._get_rally_object(result_object, model_class=testcaseresult.__class__)
        return obj

    def add_testcases_to_testset(self, testset: TestSet, testcases: list[TestCase]) -> None:
        """Add test cases to a test set"""
        tcs = [tc.ref for tc in testcases]
        self._add_members_refs_to_collection(testset.ref, tcs, "TestCases")

    def remove_testcases_from_testset(self, testset: TestSet, testcases: list[TestCase]) -> None:
        """Remove test cases from a test set"""
        tcs = [tc.ref for tc in testcases]
        self._delete_members_refs_from_collection(testset.ref, tcs, "TestCases")

    def update_tcr(self, tcr_model: TestCaseResult, body_keys: list[str] = None) -> TestCaseResult:
        key_set: set = set(body_keys) if body_keys else set()
        result_object: dict = self._update_from_dump(
            tcr_model.dump_for_update(body_keys=key_set),
            type_names.TESTCASERESULT,
        )
        return self._get_rally_object(result_object, TestCaseResult)
