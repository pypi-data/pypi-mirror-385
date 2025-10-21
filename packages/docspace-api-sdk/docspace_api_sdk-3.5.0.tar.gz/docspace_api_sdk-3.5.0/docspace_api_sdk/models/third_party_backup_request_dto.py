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
from typing import Optional, Set
from typing_extensions import Self

class ThirdPartyBackupRequestDto(BaseModel):
    """
    The third-party backup request parameters.
    """ # noqa: E501
    url: Optional[StrictStr] = Field(default=None, description="The connection URL for the sharepoint.")
    login: Optional[StrictStr] = Field(default=None, description="The login.")
    password: Optional[StrictStr] = Field(default=None, description="The password.")
    token: Optional[StrictStr] = Field(default=None, description="The authentication token.")
    customer_title: Optional[StrictStr] = Field(default=None, description="The customer title.", alias="customerTitle")
    provider_key: Optional[StrictStr] = Field(default=None, description="The provider key.", alias="providerKey")
    __properties: ClassVar[List[str]] = ["url", "login", "password", "token", "customerTitle", "providerKey"]

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
        """Create an instance of ThirdPartyBackupRequestDto from a JSON string"""
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
        # set to None if url (nullable) is None
        # and model_fields_set contains the field
        if self.url is None and "url" in self.model_fields_set:
            _dict['url'] = None

        # set to None if login (nullable) is None
        # and model_fields_set contains the field
        if self.login is None and "login" in self.model_fields_set:
            _dict['login'] = None

        # set to None if password (nullable) is None
        # and model_fields_set contains the field
        if self.password is None and "password" in self.model_fields_set:
            _dict['password'] = None

        # set to None if token (nullable) is None
        # and model_fields_set contains the field
        if self.token is None and "token" in self.model_fields_set:
            _dict['token'] = None

        # set to None if customer_title (nullable) is None
        # and model_fields_set contains the field
        if self.customer_title is None and "customer_title" in self.model_fields_set:
            _dict['customerTitle'] = None

        # set to None if provider_key (nullable) is None
        # and model_fields_set contains the field
        if self.provider_key is None and "provider_key" in self.model_fields_set:
            _dict['providerKey'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ThirdPartyBackupRequestDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "url": obj.get("url"),
            "login": obj.get("login"),
            "password": obj.get("password"),
            "token": obj.get("token"),
            "customerTitle": obj.get("customerTitle"),
            "providerKey": obj.get("providerKey")
        })
        return _obj


