import os
import sys
from logging import getLogger
from typing import List, Optional, cast

import urllib3

from rallycli.models.models import Iteration, Milestone

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rallycli.base_api import BaseAPI
from rallycli.models import RallyTypeGeneric, type_names

# logger definition
logger = getLogger(__name__)
# Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class TimeboxAPI(BaseAPI):
    """Class for accessing Time Boxes domain"""

    # Releases

    def get_releases_for_project(
        self, project_ref: str, fetch: str = "true"
    ) -> List[RallyTypeGeneric]:
        return self.query(f"(Project = {project_ref})", type_names.RELEASE, fetch=fetch)

    # Iterations

    def get_active_iterations_for_project(
        self, project_ref: str, fetch: str = "true"
    ) -> List[Iteration]:
        return self.query(
            f"( (Project = {project_ref}) AND (State != Accepted))",
            rally_type=type_names.ITERATION,
            fetch=fetch,
            model_class=Iteration,
        )

    def get_last_ended_iteration_for_project(
        self, project_ref: str, fetch: str = "true"
    ) -> Optional[Iteration]:
        """Get the last ended iteration for a given project reference."""
        result_lst: List[Iteration] = self.query(
            query=f"((Project = {project_ref}) AND (State = Accepted))",
            order_by="EndDate desc",
            pagesize=1,
            limit=1,
            rally_type=type_names.ITERATION,
            fetch=fetch,
            model_class=Iteration,
        )
        if result_lst:
            return cast(Iteration, result_lst[0])
        else:
            return None

    # * MILESTONES

    def get_milestone_by_ref(self, milestone_ref: str) -> Milestone:
        """Get Milestone by its reference"""
        abs_ref = self._get_absolute_url_from_ref(milestone_ref)
        return self.get_element_by_ref(abs_ref, model_class=Milestone)

    def get_milestone_by_formattedid(self, formattedid: str) -> Optional[Milestone]:
        """Get Milestone by its FormattedID"""
        result_lst: List[RallyTypeGeneric] = self.query(
            f"(FormattedID = {formattedid})", type_names.MILESTONE, model_class=Milestone
        )
        if result_lst:
            return cast(Milestone, result_lst[0])
        else:
            return None

    def get_milestone_by_name(self, name: str, project_ref: str) -> Optional[Milestone]:
        """Get Milestone by its Name"""
        result_lst: List[RallyTypeGeneric] = self.query(
            f"(Name = {name})", type_names.MILESTONE, model_class=Milestone, project=project_ref
        )
        if result_lst:
            return cast(Milestone, result_lst[0])
        else:
            return None

    def get_milestones_for_project(self, project_ref: str, fetch: str = "true") -> List[Milestone]:
        """Get all milestones for a given project reference"""
        # Get absolute reference for the project
        project_abs_ref = self._baseurl + project_ref[1:]
        return self.query(
            f'(Projects contains "{project_abs_ref}")',
            type_names.MILESTONE,
            fetch=fetch,
            project=project_ref,
        )

    def get_last_ended_milestone_for_project(
        self, project_ref: str, fetch: str = "true"
    ) -> Optional[Milestone]:
        """Get the last ended milestone for a given project reference."""
        result_lst: List[Milestone] = self.query(
            query=f"(Project = {project_ref} AND TargetDate < 'today')",
            order_by="TargetDate desc",
            pagesize=1,
            limit=1,
            rally_type=type_names.MILESTONE,
            fetch=fetch,
            model_class=Milestone,
        )
        if result_lst:
            return cast(Iteration, result_lst[0])
        else:
            return None

    def create_milestone(self, milestone: Milestone) -> Milestone:
        created: dict = self._create_from_dump(
            milestone.dump_for_create(), rally_type=type_names.MILESTONE
        )
        return Milestone(**created)

    def add_userstories_to_milestone(self, milestone: Milestone, us_refs: list[str]):
        self._add_members_refs_to_collection(milestone.ref, us_refs, "Artifacts")

    def remove_userstories_from_milestone(self, milestone: Milestone, us_refs: list[str]):
        """Remove user stories from a milestone."""
        self._delete_members_refs_from_collection(milestone.ref, us_refs, "Artifacts")

    def add_testsets_to_milestone(self, milestone: Milestone, testset_refs: list[str]):
        self._add_members_refs_to_collection(milestone.ref, testset_refs, "Artifacts")

    def remove_testsets_from_milestone(self, milestone: Milestone, testset_refs: list[str]):
        """Remove test sets from a milestone."""
        self._delete_members_refs_from_collection(milestone.ref, testset_refs, "Artifacts")
