import asyncio
from logging import getLogger
from typing import List, Optional, Tuple, Literal

import urllib3

from rallycli import BaseAPI
from rallycli.models import User, type_names
from rallycli.models.models import ProjectPermission

# logger definition
logger = getLogger(__name__)
# Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class UserAPI(BaseAPI):
    """Client class for accessing User model for Rally Software API."""

    def get_this_user(self):
        user: User = self.get_element_by_ref(f"{self._baseurl}user", model_class=User)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        query: str = f"( UserName = {username} )"
        users: List[User] = self.query(query, "user", model_class=User)
        if not users:
            logger.warning(f"User with UserName: '{username}' NOT found")
            return None
        return users[0]

    def create_user(self, user_model: User) -> Optional[User]:
        """Create user"""
        result_object: dict = self._create_from_dump(user_model.dump_for_create(), type_names.USER)
        return self._get_rally_object(result_object, User)

    def update_user(self, user_model: User, body_keys: List[str] = None) -> Optional[User]:
        """Update user"""
        key_set: set = set(body_keys) if body_keys else set()
        result_object: dict = self._update_from_dump(
            user_model.dump_for_update(body_keys=key_set),
            type_names.USER,
        )
        return self._get_rally_object(result_object, User)

    def update_user_list(
        self, user_lst: List[User], body_keys: List[str] = None
    ) -> Optional[List[User]]:
        """Async IO update of a list of users. User objects new _ref field to be updated"""
        key_set: set = set(body_keys) if body_keys else set()
        # List of Tuple [url, update_data]
        url_data: List[Tuple[str, dict]] = []
        for user in user_lst:
            url: str = f"{user.ref}{BaseAPI._security_key}"
            data: dict = {"user": user.dump_for_update(body_keys=key_set)}
            url_data.append((url, data))

        result_objects: List[dict] = asyncio.run(self._async_post_elements(url_data))
        objs: List[User] = [User.model_validate(robj) for robj in result_objects]
        return objs

    def add_user_to_project_membership(self, user_ref: str, project_ref: str):
        """TODO Review"""
        self._add_members_refs_to_collection(project_ref, [user_ref], "TeamMembers")

    def add_user_permission_for_project(
        self, user_ref: str, project_ref: str, perm: Literal["Viewer", "Editor", "Admin"]
    ):
        """TODO ... Review sample project permission
                {
                "..."
                "Name": "Team.Batch SSMM - Iteration Admin",
                "Role": "Admin",
                "User": {
                        "_rallyAPIMajor": "2",
                        "_rallyAPIMinor": "0",
                        "_ref": "https://eu1.rallydev.com/slm/webservice/v2.0/user/66496867629",
                        "_refObjectUUID": "4d474805-6d63-4115-85d8-4c546eb6b361",
                        "_refObjectName": "Andrés Guerrero",
                        "_type": "User"
                },
                "Project": {
                        "_rallyAPIMajor": "2",
                        "_rallyAPIMinor": "0",
                        "_ref": "https://eu1.rallydev.com/slm/webservice/v2.0/project/66843277101",
                        "_refObjectUUID": "25f7c497-ab63-4a33-84fc-4d3e9c9f7d9c",
                        "_refObjectName": "Team.Batch SSMM - Iteration",
                        "_type": "Project"
                },
                "_type": "ProjectPermission"
        },

        """
        project_perm = ProjectPermission(User=user_ref, Project=project_ref, Role=perm)
        result_object: dict = self._create_from_dump(
            project_perm.dump_for_create(), type_names.PROJECT_PERMISSION
        )
        return self._get_rally_object(result_object, ProjectPermission)
