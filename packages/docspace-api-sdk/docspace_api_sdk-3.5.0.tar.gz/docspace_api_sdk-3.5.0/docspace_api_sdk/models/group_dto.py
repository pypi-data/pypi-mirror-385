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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_full_dto import EmployeeFullDto
from typing import Optional, Set
from typing_extensions import Self

class GroupDto(BaseModel):
    """
    The group parameters.
    """ # noqa: E501
    name: Optional[StrictStr] = Field(description="The group name.")
    parent: Optional[StrictStr] = Field(default=None, description="The parent group ID.")
    category: StrictStr = Field(description="The group category ID.")
    id: StrictStr = Field(description="The group ID.")
    is_ldap: StrictBool = Field(description="Specifies if the LDAP settings are enabled for the group or not.", alias="isLDAP")
    is_system: Optional[StrictBool] = Field(default=None, description="Indicates whether the group is a system group.", alias="isSystem")
    manager: Optional[EmployeeFullDto] = None
    members: Optional[List[EmployeeFullDto]] = Field(default=None, description="The list of group members.")
    shared: Optional[StrictBool] = Field(default=None, description="Specifies whether the group can be shared or not.")
    members_count: Optional[StrictInt] = Field(default=None, description="The number of group members.", alias="membersCount")
    __properties: ClassVar[List[str]] = ["name", "parent", "category", "id", "isLDAP", "isSystem", "manager", "members", "shared", "membersCount"]

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
        """Create an instance of GroupDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of manager
        if self.manager:
            _dict['manager'] = self.manager.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in members (list)
        _items = []
        if self.members:
            for _item_members in self.members:
                if _item_members:
                    _items.append(_item_members.to_dict())
            _dict['members'] = _items
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if parent (nullable) is None
        # and model_fields_set contains the field
        if self.parent is None and "parent" in self.model_fields_set:
            _dict['parent'] = None

        # set to None if is_system (nullable) is None
        # and model_fields_set contains the field
        if self.is_system is None and "is_system" in self.model_fields_set:
            _dict['isSystem'] = None

        # set to None if members (nullable) is None
        # and model_fields_set contains the field
        if self.members is None and "members" in self.model_fields_set:
            _dict['members'] = None

        # set to None if shared (nullable) is None
        # and model_fields_set contains the field
        if self.shared is None and "shared" in self.model_fields_set:
            _dict['shared'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of GroupDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "parent": obj.get("parent"),
            "category": obj.get("category"),
            "id": obj.get("id"),
            "isLDAP": obj.get("isLDAP"),
            "isSystem": obj.get("isSystem"),
            "manager": EmployeeFullDto.from_dict(obj["manager"]) if obj.get("manager") is not None else None,
            "members": [EmployeeFullDto.from_dict(_item) for _item in obj["members"]] if obj.get("members") is not None else None,
            "shared": obj.get("shared"),
            "membersCount": obj.get("membersCount")
        })
        return _obj


