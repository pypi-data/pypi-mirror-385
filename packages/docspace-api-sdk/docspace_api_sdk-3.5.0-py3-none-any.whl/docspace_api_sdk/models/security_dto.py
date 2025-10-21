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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_dto import EmployeeDto
from docspace_api_sdk.models.group_summary_dto import GroupSummaryDto
from typing import Optional, Set
from typing_extensions import Self

class SecurityDto(BaseModel):
    """
    The security information.
    """ # noqa: E501
    web_item_id: Optional[StrictStr] = Field(default=None, description="The module ID.", alias="webItemId")
    users: Optional[List[EmployeeDto]] = Field(default=None, description="The list of users with the access to the module.")
    groups: Optional[List[GroupSummaryDto]] = Field(default=None, description="The list of groups with the access to the module.")
    enabled: Optional[StrictBool] = Field(default=None, description="Specifies if the security settings are enabled or not.")
    is_sub_item: Optional[StrictBool] = Field(default=None, description="Specifies if the module is a subitem or not.", alias="isSubItem")
    __properties: ClassVar[List[str]] = ["webItemId", "users", "groups", "enabled", "isSubItem"]

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
        """Create an instance of SecurityDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in users (list)
        _items = []
        if self.users:
            for _item_users in self.users:
                if _item_users:
                    _items.append(_item_users.to_dict())
            _dict['users'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in groups (list)
        _items = []
        if self.groups:
            for _item_groups in self.groups:
                if _item_groups:
                    _items.append(_item_groups.to_dict())
            _dict['groups'] = _items
        # set to None if web_item_id (nullable) is None
        # and model_fields_set contains the field
        if self.web_item_id is None and "web_item_id" in self.model_fields_set:
            _dict['webItemId'] = None

        # set to None if users (nullable) is None
        # and model_fields_set contains the field
        if self.users is None and "users" in self.model_fields_set:
            _dict['users'] = None

        # set to None if groups (nullable) is None
        # and model_fields_set contains the field
        if self.groups is None and "groups" in self.model_fields_set:
            _dict['groups'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SecurityDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "webItemId": obj.get("webItemId"),
            "users": [EmployeeDto.from_dict(_item) for _item in obj["users"]] if obj.get("users") is not None else None,
            "groups": [GroupSummaryDto.from_dict(_item) for _item in obj["groups"]] if obj.get("groups") is not None else None,
            "enabled": obj.get("enabled"),
            "isSubItem": obj.get("isSubItem")
        })
        return _obj


