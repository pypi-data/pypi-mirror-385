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
from typing import Optional, Set
from typing_extensions import Self

class GroupMemberSecurityRequestDto(BaseModel):
    """
    The group member security information.
    """ # noqa: E501
    user: EmployeeFullDto
    group_access: FileShare = Field(alias="groupAccess")
    user_access: Optional[FileShare] = Field(default=None, alias="userAccess")
    overridden: StrictBool = Field(description="Specifies if the group access rights are overridden or not.")
    can_edit_access: StrictBool = Field(description="Specifies if the group member can edit the group access rights or not.", alias="canEditAccess")
    owner: StrictBool = Field(description="Specifies if the group member is a group owner or not.")
    __properties: ClassVar[List[str]] = ["user", "groupAccess", "userAccess", "overridden", "canEditAccess", "owner"]

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
        """Create an instance of GroupMemberSecurityRequestDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of GroupMemberSecurityRequestDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "user": EmployeeFullDto.from_dict(obj["user"]) if obj.get("user") is not None else None,
            "groupAccess": obj.get("groupAccess"),
            "userAccess": obj.get("userAccess"),
            "overridden": obj.get("overridden"),
            "canEditAccess": obj.get("canEditAccess"),
            "owner": obj.get("owner")
        })
        return _obj


