#
# (c) Copyright Ascensio System SIA 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_full_dto import EmployeeFullDto
from docspace_api_sdk.models.file_share import FileShare
from docspace_api_sdk.models.file_share_link import FileShareLink
from docspace_api_sdk.models.group_summary_dto import GroupSummaryDto
from docspace_api_sdk.models.subject_type import SubjectType
from typing import Optional, Set
from typing_extensions import Self

class FileShareDto(BaseModel):
    """
    The file sharing information and access rights.
    """ # noqa: E501
    access: Optional[FileShare] = None
    shared_to: Optional[Any] = Field(default=None, description="The user who has the access to the specified file.", alias="sharedTo")
    shared_to_user: Optional[EmployeeFullDto] = Field(default=None, alias="sharedToUser")
    shared_to_group: Optional[GroupSummaryDto] = Field(default=None, alias="sharedToGroup")
    shared_link: Optional[FileShareLink] = Field(default=None, alias="sharedLink")
    is_locked: StrictBool = Field(description="Specifies if the access right is locked or not.", alias="isLocked")
    is_owner: StrictBool = Field(description="Specifies if the user is an owner of the specified file or not.", alias="isOwner")
    can_edit_access: StrictBool = Field(description="Specifies if the user can edit the access to the specified file or not.", alias="canEditAccess")
    can_edit_internal: StrictBool = Field(description="Indicates whether internal editing permissions are granted.", alias="canEditInternal")
    can_edit_deny_download: StrictBool = Field(description="Determines whether the user has permission to modify the deny download setting for the file share.", alias="canEditDenyDownload")
    can_edit_expiration_date: StrictBool = Field(description="Indicates whether the expiration date of access permissions can be edited.", alias="canEditExpirationDate")
    can_revoke: StrictBool = Field(description="Specifies whether the file sharing access can be revoked by the current user.", alias="canRevoke")
    subject_type: SubjectType = Field(alias="subjectType")
    __properties: ClassVar[List[str]] = ["access", "sharedTo", "sharedToUser", "sharedToGroup", "sharedLink", "isLocked", "isOwner", "canEditAccess", "canEditInternal", "canEditDenyDownload", "canEditExpirationDate", "canRevoke", "subjectType"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of FileShareDto from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of shared_to_user
        if self.shared_to_user:
            _dict['sharedToUser'] = self.shared_to_user.to_dict()
        # override the default output from pydantic by calling `to_dict()` of shared_to_group
        if self.shared_to_group:
            _dict['sharedToGroup'] = self.shared_to_group.to_dict()
        # override the default output from pydantic by calling `to_dict()` of shared_link
        if self.shared_link:
            _dict['sharedLink'] = self.shared_link.to_dict()
        # set to None if shared_to (nullable) is None
        # and model_fields_set contains the field
        if self.shared_to is None and "shared_to" in self.model_fields_set:
            _dict['sharedTo'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FileShareDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "access": obj.get("access"),
            "sharedTo": obj.get("sharedTo"),
            "sharedToUser": EmployeeFullDto.from_dict(obj["sharedToUser"]) if obj.get("sharedToUser") is not None else None,
            "sharedToGroup": GroupSummaryDto.from_dict(obj["sharedToGroup"]) if obj.get("sharedToGroup") is not None else None,
            "sharedLink": FileShareLink.from_dict(obj["sharedLink"]) if obj.get("sharedLink") is not None else None,
            "isLocked": obj.get("isLocked"),
            "isOwner": obj.get("isOwner"),
            "canEditAccess": obj.get("canEditAccess"),
            "canEditInternal": obj.get("canEditInternal"),
            "canEditDenyDownload": obj.get("canEditDenyDownload"),
            "canEditExpirationDate": obj.get("canEditExpirationDate"),
            "canRevoke": obj.get("canRevoke"),
            "subjectType": obj.get("subjectType")
        })
        return _obj


