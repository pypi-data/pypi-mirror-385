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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.auth_data import AuthData
from typing import Optional, Set
from typing_extensions import Self

class ThirdPartyParams(BaseModel):
    """
    The third-party account parameters.
    """ # noqa: E501
    auth_data: Optional[AuthData] = None
    corporate: Optional[StrictBool] = Field(default=None, description="Specifies if this is a corporate account or not.")
    rooms_storage: Optional[StrictBool] = Field(default=None, description="Specifies if this is a room storage or not.", alias="roomsStorage")
    customer_title: Optional[StrictStr] = Field(default=None, description="The customer title.")
    provider_id: Optional[StrictInt] = Field(default=None, description="The provider ID.")
    provider_key: Optional[StrictStr] = Field(default=None, description="The provider key.")
    __properties: ClassVar[List[str]] = ["auth_data", "corporate", "roomsStorage", "customer_title", "provider_id", "provider_key"]

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
        """Create an instance of ThirdPartyParams from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of auth_data
        if self.auth_data:
            _dict['auth_data'] = self.auth_data.to_dict()
        # set to None if customer_title (nullable) is None
        # and model_fields_set contains the field
        if self.customer_title is None and "customer_title" in self.model_fields_set:
            _dict['customer_title'] = None

        # set to None if provider_id (nullable) is None
        # and model_fields_set contains the field
        if self.provider_id is None and "provider_id" in self.model_fields_set:
            _dict['provider_id'] = None

        # set to None if provider_key (nullable) is None
        # and model_fields_set contains the field
        if self.provider_key is None and "provider_key" in self.model_fields_set:
            _dict['provider_key'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ThirdPartyParams from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "auth_data": AuthData.from_dict(obj["auth_data"]) if obj.get("auth_data") is not None else None,
            "corporate": obj.get("corporate"),
            "roomsStorage": obj.get("roomsStorage"),
            "customer_title": obj.get("customer_title"),
            "provider_id": obj.get("provider_id"),
            "provider_key": obj.get("provider_key")
        })
        return _obj


