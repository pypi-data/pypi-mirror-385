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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_type import EmployeeType
from typing import Optional, Set
from typing_extensions import Self

class SignupAccountRequestDto(BaseModel):
    """
    The request parameters for creating a third-party account.
    """ # noqa: E501
    employee_type: Optional[EmployeeType] = Field(default=None, alias="employeeType")
    first_name: Optional[StrictStr] = Field(default=None, description="The user first name.", alias="firstName")
    last_name: Optional[StrictStr] = Field(default=None, description="The user last name.", alias="lastName")
    email: Optional[StrictStr] = Field(default=None, description="The user email address.")
    password_hash: Optional[StrictStr] = Field(default=None, description="The user password hash.", alias="passwordHash")
    key: Optional[StrictStr] = Field(description="The user link key.")
    culture: Optional[StrictStr] = Field(default=None, description="The user culture code.")
    serialized_profile: Optional[StrictStr] = Field(description="The third-party profile in the serialized format", alias="serializedProfile")
    __properties: ClassVar[List[str]] = ["employeeType", "firstName", "lastName", "email", "passwordHash", "key", "culture", "serializedProfile"]

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
        """Create an instance of SignupAccountRequestDto from a JSON string"""
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
        # set to None if first_name (nullable) is None
        # and model_fields_set contains the field
        if self.first_name is None and "first_name" in self.model_fields_set:
            _dict['firstName'] = None

        # set to None if last_name (nullable) is None
        # and model_fields_set contains the field
        if self.last_name is None and "last_name" in self.model_fields_set:
            _dict['lastName'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if password_hash (nullable) is None
        # and model_fields_set contains the field
        if self.password_hash is None and "password_hash" in self.model_fields_set:
            _dict['passwordHash'] = None

        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if culture (nullable) is None
        # and model_fields_set contains the field
        if self.culture is None and "culture" in self.model_fields_set:
            _dict['culture'] = None

        # set to None if serialized_profile (nullable) is None
        # and model_fields_set contains the field
        if self.serialized_profile is None and "serialized_profile" in self.model_fields_set:
            _dict['serializedProfile'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SignupAccountRequestDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "employeeType": obj.get("employeeType"),
            "firstName": obj.get("firstName"),
            "lastName": obj.get("lastName"),
            "email": obj.get("email"),
            "passwordHash": obj.get("passwordHash"),
            "key": obj.get("key"),
            "culture": obj.get("culture"),
            "serializedProfile": obj.get("serializedProfile")
        })
        return _obj


