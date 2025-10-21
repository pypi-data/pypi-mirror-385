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
from typing import Optional, Set
from typing_extensions import Self

class FormRole(BaseModel):
    """
    The form role.
    """ # noqa: E501
    room_id: Optional[StrictInt] = Field(default=None, description="The room ID.", alias="roomId")
    role_name: Optional[StrictStr] = Field(default=None, description="The role name.", alias="roleName")
    role_color: Optional[StrictStr] = Field(default=None, description="The role color.", alias="roleColor")
    user_id: Optional[StrictStr] = Field(default=None, description="The user ID.", alias="userId")
    sequence: Optional[StrictInt] = Field(default=None, description="The role sequence.")
    submitted: Optional[StrictBool] = Field(default=None, description="Specifies if the role was submitted or not.")
    opened_at: Optional[datetime] = Field(default=None, description="The date and time when the role was opened.", alias="openedAt")
    submission_date: Optional[datetime] = Field(default=None, description="The date and time when the role was submitted.", alias="submissionDate")
    __properties: ClassVar[List[str]] = ["roomId", "roleName", "roleColor", "userId", "sequence", "submitted", "openedAt", "submissionDate"]

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
        """Create an instance of FormRole from a JSON string"""
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
        # set to None if role_name (nullable) is None
        # and model_fields_set contains the field
        if self.role_name is None and "role_name" in self.model_fields_set:
            _dict['roleName'] = None

        # set to None if role_color (nullable) is None
        # and model_fields_set contains the field
        if self.role_color is None and "role_color" in self.model_fields_set:
            _dict['roleColor'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FormRole from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "roomId": obj.get("roomId"),
            "roleName": obj.get("roleName"),
            "roleColor": obj.get("roleColor"),
            "userId": obj.get("userId"),
            "sequence": obj.get("sequence"),
            "submitted": obj.get("submitted"),
            "openedAt": obj.get("openedAt"),
            "submissionDate": obj.get("submissionDate")
        })
        return _obj


