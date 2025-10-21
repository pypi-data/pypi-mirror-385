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
from docspace_api_sdk.models.confirm_data import ConfirmData
from docspace_api_sdk.models.recaptcha_type import RecaptchaType
from typing import Optional, Set
from typing_extensions import Self

class AuthRequestsDto(BaseModel):
    """
    The parameters required for the user authentication requests.
    """ # noqa: E501
    user_name: Optional[StrictStr] = Field(default=None, description="The username or email used for authentication.", alias="userName")
    password: Optional[StrictStr] = Field(default=None, description="The password in plain text for user authentication.")
    password_hash: Optional[StrictStr] = Field(default=None, description="The hashed password for secure verification.", alias="passwordHash")
    provider: Optional[StrictStr] = Field(default=None, description="The type of authentication provider (e.g., internal, Google, Azure).")
    access_token: Optional[StrictStr] = Field(default=None, description="The access token used for authentication with external providers.", alias="accessToken")
    serialized_profile: Optional[StrictStr] = Field(default=None, description="The serialized user profile data, if applicable.", alias="serializedProfile")
    code: Optional[StrictStr] = Field(default=None, description="The code for two-factor authentication.")
    code_o_auth: Optional[StrictStr] = Field(default=None, description="The authorization code used for obtaining OAuth tokens.", alias="codeOAuth")
    session: Optional[StrictBool] = Field(default=None, description="Specifies whether the authentication is session-based.")
    confirm_data: Optional[ConfirmData] = Field(default=None, alias="confirmData")
    recaptcha_type: Optional[RecaptchaType] = Field(default=None, alias="recaptchaType")
    recaptcha_response: Optional[StrictStr] = Field(default=None, description="The user's response to the CAPTCHA challenge.", alias="recaptchaResponse")
    culture: Optional[StrictStr] = Field(default=None, description="The culture code for localization during authentication.")
    __properties: ClassVar[List[str]] = ["userName", "password", "passwordHash", "provider", "accessToken", "serializedProfile", "code", "codeOAuth", "session", "confirmData", "recaptchaType", "recaptchaResponse", "culture"]

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
        """Create an instance of AuthRequestsDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of confirm_data
        if self.confirm_data:
            _dict['confirmData'] = self.confirm_data.to_dict()
        # set to None if user_name (nullable) is None
        # and model_fields_set contains the field
        if self.user_name is None and "user_name" in self.model_fields_set:
            _dict['userName'] = None

        # set to None if password (nullable) is None
        # and model_fields_set contains the field
        if self.password is None and "password" in self.model_fields_set:
            _dict['password'] = None

        # set to None if password_hash (nullable) is None
        # and model_fields_set contains the field
        if self.password_hash is None and "password_hash" in self.model_fields_set:
            _dict['passwordHash'] = None

        # set to None if provider (nullable) is None
        # and model_fields_set contains the field
        if self.provider is None and "provider" in self.model_fields_set:
            _dict['provider'] = None

        # set to None if access_token (nullable) is None
        # and model_fields_set contains the field
        if self.access_token is None and "access_token" in self.model_fields_set:
            _dict['accessToken'] = None

        # set to None if serialized_profile (nullable) is None
        # and model_fields_set contains the field
        if self.serialized_profile is None and "serialized_profile" in self.model_fields_set:
            _dict['serializedProfile'] = None

        # set to None if code (nullable) is None
        # and model_fields_set contains the field
        if self.code is None and "code" in self.model_fields_set:
            _dict['code'] = None

        # set to None if code_o_auth (nullable) is None
        # and model_fields_set contains the field
        if self.code_o_auth is None and "code_o_auth" in self.model_fields_set:
            _dict['codeOAuth'] = None

        # set to None if recaptcha_response (nullable) is None
        # and model_fields_set contains the field
        if self.recaptcha_response is None and "recaptcha_response" in self.model_fields_set:
            _dict['recaptchaResponse'] = None

        # set to None if culture (nullable) is None
        # and model_fields_set contains the field
        if self.culture is None and "culture" in self.model_fields_set:
            _dict['culture'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AuthRequestsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "userName": obj.get("userName"),
            "password": obj.get("password"),
            "passwordHash": obj.get("passwordHash"),
            "provider": obj.get("provider"),
            "accessToken": obj.get("accessToken"),
            "serializedProfile": obj.get("serializedProfile"),
            "code": obj.get("code"),
            "codeOAuth": obj.get("codeOAuth"),
            "session": obj.get("session"),
            "confirmData": ConfirmData.from_dict(obj["confirmData"]) if obj.get("confirmData") is not None else None,
            "recaptchaType": obj.get("recaptchaType"),
            "recaptchaResponse": obj.get("recaptchaResponse"),
            "culture": obj.get("culture")
        })
        return _obj


