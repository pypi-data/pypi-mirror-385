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
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.employee_dto import EmployeeDto
from typing import Optional, Set
from typing_extensions import Self

class ApiKeyResponseDto(BaseModel):
    """
    The response data for the API key operations.
    """ # noqa: E501
    id: StrictStr = Field(description="The API key unique identifier.")
    name: Optional[StrictStr] = Field(description="The API key name.")
    key: Optional[StrictStr] = Field(description="The full API key value (only returned when creating a new key).")
    key_postfix: Optional[StrictStr] = Field(default=None, description="The API key postfix (used for identification).", alias="keyPostfix")
    permissions: Optional[List[StrictStr]] = Field(description="The list of permissions granted to the API key.")
    last_used: Optional[ApiDateTime] = Field(default=None, alias="lastUsed")
    create_on: Optional[ApiDateTime] = Field(default=None, alias="createOn")
    create_by: Optional[EmployeeDto] = Field(default=None, alias="createBy")
    expires_at: Optional[ApiDateTime] = Field(default=None, alias="expiresAt")
    is_active: StrictBool = Field(description="Indicates whether the API key is active or not.", alias="isActive")
    __properties: ClassVar[List[str]] = ["id", "name", "key", "keyPostfix", "permissions", "lastUsed", "createOn", "createBy", "expiresAt", "isActive"]

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
        """Create an instance of ApiKeyResponseDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of last_used
        if self.last_used:
            _dict['lastUsed'] = self.last_used.to_dict()
        # override the default output from pydantic by calling `to_dict()` of create_on
        if self.create_on:
            _dict['createOn'] = self.create_on.to_dict()
        # override the default output from pydantic by calling `to_dict()` of create_by
        if self.create_by:
            _dict['createBy'] = self.create_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of expires_at
        if self.expires_at:
            _dict['expiresAt'] = self.expires_at.to_dict()
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if key_postfix (nullable) is None
        # and model_fields_set contains the field
        if self.key_postfix is None and "key_postfix" in self.model_fields_set:
            _dict['keyPostfix'] = None

        # set to None if permissions (nullable) is None
        # and model_fields_set contains the field
        if self.permissions is None and "permissions" in self.model_fields_set:
            _dict['permissions'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ApiKeyResponseDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "key": obj.get("key"),
            "keyPostfix": obj.get("keyPostfix"),
            "permissions": obj.get("permissions"),
            "lastUsed": ApiDateTime.from_dict(obj["lastUsed"]) if obj.get("lastUsed") is not None else None,
            "createOn": ApiDateTime.from_dict(obj["createOn"]) if obj.get("createOn") is not None else None,
            "createBy": EmployeeDto.from_dict(obj["createBy"]) if obj.get("createBy") is not None else None,
            "expiresAt": ApiDateTime.from_dict(obj["expiresAt"]) if obj.get("expiresAt") is not None else None,
            "isActive": obj.get("isActive")
        })
        return _obj


