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
from typing import Optional, Set
from typing_extensions import Self

class ProviderDto(BaseModel):
    """
    The provider information.
    """ # noqa: E501
    name: Optional[StrictStr] = Field(default=None, description="The provider name.")
    key: Optional[StrictStr] = Field(default=None, description="The provider key.")
    connected: Optional[StrictBool] = Field(default=None, description="Specifies whether the provider is connected.")
    oauth: Optional[StrictBool] = Field(default=None, description="Specifies if the provider is OAuth.")
    redirect_url: Optional[StrictStr] = Field(default=None, description="The provider redirect URL.", alias="redirectUrl")
    required_connection_url: Optional[StrictBool] = Field(default=None, description="The required connection URL flag.", alias="requiredConnectionUrl")
    client_id: Optional[StrictStr] = Field(default=None, description="The provider OAuth client ID.", alias="clientId")
    __properties: ClassVar[List[str]] = ["name", "key", "connected", "oauth", "redirectUrl", "requiredConnectionUrl", "clientId"]

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
        """Create an instance of ProviderDto from a JSON string"""
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
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if redirect_url (nullable) is None
        # and model_fields_set contains the field
        if self.redirect_url is None and "redirect_url" in self.model_fields_set:
            _dict['redirectUrl'] = None

        # set to None if client_id (nullable) is None
        # and model_fields_set contains the field
        if self.client_id is None and "client_id" in self.model_fields_set:
            _dict['clientId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ProviderDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "key": obj.get("key"),
            "connected": obj.get("connected"),
            "oauth": obj.get("oauth"),
            "redirectUrl": obj.get("redirectUrl"),
            "requiredConnectionUrl": obj.get("requiredConnectionUrl"),
            "clientId": obj.get("clientId")
        })
        return _obj


