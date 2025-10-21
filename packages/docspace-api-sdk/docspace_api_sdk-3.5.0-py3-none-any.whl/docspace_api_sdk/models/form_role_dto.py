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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_full_dto import EmployeeFullDto
from docspace_api_sdk.models.form_filling_status import FormFillingStatus
from typing import Optional, Set
from typing_extensions import Self

class FormRoleDto(BaseModel):
    """
    The form role parameters.
    """ # noqa: E501
    role_name: Optional[StrictStr] = Field(description="The role name.", alias="roleName")
    role_color: Optional[StrictStr] = Field(default=None, description="The role color.", alias="roleColor")
    user: Optional[EmployeeFullDto] = None
    sequence: StrictInt = Field(description="The role sequence.")
    submitted: StrictBool = Field(description="Specifies if the role is submitted.")
    stoped_by: Optional[EmployeeFullDto] = Field(default=None, alias="stopedBy")
    history: Optional[Dict[str, datetime]] = Field(default=None, description="The role history.")
    role_status: Optional[FormFillingStatus] = Field(default=None, alias="roleStatus")
    __properties: ClassVar[List[str]] = ["roleName", "roleColor", "user", "sequence", "submitted", "stopedBy", "history", "roleStatus"]

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
        """Create an instance of FormRoleDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of stoped_by
        if self.stoped_by:
            _dict['stopedBy'] = self.stoped_by.to_dict()
        # set to None if role_name (nullable) is None
        # and model_fields_set contains the field
        if self.role_name is None and "role_name" in self.model_fields_set:
            _dict['roleName'] = None

        # set to None if role_color (nullable) is None
        # and model_fields_set contains the field
        if self.role_color is None and "role_color" in self.model_fields_set:
            _dict['roleColor'] = None

        # set to None if history (nullable) is None
        # and model_fields_set contains the field
        if self.history is None and "history" in self.model_fields_set:
            _dict['history'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FormRoleDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "roleName": obj.get("roleName"),
            "roleColor": obj.get("roleColor"),
            "user": EmployeeFullDto.from_dict(obj["user"]) if obj.get("user") is not None else None,
            "sequence": obj.get("sequence"),
            "submitted": obj.get("submitted"),
            "stopedBy": EmployeeFullDto.from_dict(obj["stopedBy"]) if obj.get("stopedBy") is not None else None,
            "history": obj.get("history"),
            "roleStatus": obj.get("roleStatus")
        })
        return _obj


