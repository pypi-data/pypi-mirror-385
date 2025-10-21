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
from docspace_api_sdk.models.confirm_type import ConfirmType
from docspace_api_sdk.models.employee_type import EmployeeType
from typing import Optional, Set
from typing_extensions import Self

class EmailValidationKeyModel(BaseModel):
    """
    The confirmation email parameters.
    """ # noqa: E501
    key: Optional[StrictStr] = Field(default=None, description="The email validation key.")
    empl_type: Optional[EmployeeType] = Field(default=None, alias="emplType")
    email: Optional[StrictStr] = Field(default=None, description="The email address.")
    enc_email: Optional[StrictStr] = Field(default=None, description="The encrypted email address.", alias="encEmail")
    ui_d: Optional[StrictStr] = Field(default=None, description="The user ID.", alias="uiD")
    type: Optional[ConfirmType] = None
    first: Optional[StrictStr] = Field(default=None, description="Specifies whether it is the first time account access or not.")
    room_id: Optional[StrictStr] = Field(default=None, description="The room ID.", alias="roomId")
    __properties: ClassVar[List[str]] = ["key", "emplType", "email", "encEmail", "uiD", "type", "first", "roomId"]

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
        """Create an instance of EmailValidationKeyModel from a JSON string"""
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
        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if enc_email (nullable) is None
        # and model_fields_set contains the field
        if self.enc_email is None and "enc_email" in self.model_fields_set:
            _dict['encEmail'] = None

        # set to None if ui_d (nullable) is None
        # and model_fields_set contains the field
        if self.ui_d is None and "ui_d" in self.model_fields_set:
            _dict['uiD'] = None

        # set to None if first (nullable) is None
        # and model_fields_set contains the field
        if self.first is None and "first" in self.model_fields_set:
            _dict['first'] = None

        # set to None if room_id (nullable) is None
        # and model_fields_set contains the field
        if self.room_id is None and "room_id" in self.model_fields_set:
            _dict['roomId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EmailValidationKeyModel from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "key": obj.get("key"),
            "emplType": obj.get("emplType"),
            "email": obj.get("email"),
            "encEmail": obj.get("encEmail"),
            "uiD": obj.get("uiD"),
            "type": obj.get("type"),
            "first": obj.get("first"),
            "roomId": obj.get("roomId")
        })
        return _obj


