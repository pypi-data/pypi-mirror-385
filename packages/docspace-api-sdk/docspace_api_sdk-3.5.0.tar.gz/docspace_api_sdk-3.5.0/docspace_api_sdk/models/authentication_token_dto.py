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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class AuthenticationTokenDto(BaseModel):
    """
    The authentication token parameters.
    """ # noqa: E501
    token: Optional[StrictStr] = Field(default=None, description="The authentication token.")
    expires: Optional[datetime] = Field(default=None, description="The token expiration time.")
    sms: Optional[StrictBool] = Field(default=None, description="Specifies if the authentication code is sent by SMS or not.")
    phone_noise: Optional[StrictStr] = Field(default=None, description="The phone number.", alias="phoneNoise")
    tfa: Optional[StrictBool] = Field(default=None, description="Specifies if the two-factor application is used or not.")
    tfa_key: Optional[StrictStr] = Field(default=None, description="The two-factor authentication key.", alias="tfaKey")
    confirm_url: Optional[StrictStr] = Field(default=None, description="The confirmation email URL.", alias="confirmUrl")
    __properties: ClassVar[List[str]] = ["token", "expires", "sms", "phoneNoise", "tfa", "tfaKey", "confirmUrl"]

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
        """Create an instance of AuthenticationTokenDto from a JSON string"""
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
        # set to None if token (nullable) is None
        # and model_fields_set contains the field
        if self.token is None and "token" in self.model_fields_set:
            _dict['token'] = None

        # set to None if phone_noise (nullable) is None
        # and model_fields_set contains the field
        if self.phone_noise is None and "phone_noise" in self.model_fields_set:
            _dict['phoneNoise'] = None

        # set to None if tfa_key (nullable) is None
        # and model_fields_set contains the field
        if self.tfa_key is None and "tfa_key" in self.model_fields_set:
            _dict['tfaKey'] = None

        # set to None if confirm_url (nullable) is None
        # and model_fields_set contains the field
        if self.confirm_url is None and "confirm_url" in self.model_fields_set:
            _dict['confirmUrl'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AuthenticationTokenDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "token": obj.get("token"),
            "expires": obj.get("expires"),
            "sms": obj.get("sms"),
            "phoneNoise": obj.get("phoneNoise"),
            "tfa": obj.get("tfa"),
            "tfaKey": obj.get("tfaKey"),
            "confirmUrl": obj.get("confirmUrl")
        })
        return _obj


