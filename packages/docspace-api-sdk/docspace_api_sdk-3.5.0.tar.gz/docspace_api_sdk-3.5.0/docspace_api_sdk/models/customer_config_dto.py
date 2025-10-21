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

class CustomerConfigDto(BaseModel):
    """
    The customer config parameters.
    """ # noqa: E501
    address: Optional[StrictStr] = Field(default=None, description="The address of the customer configuration.")
    logo: Optional[StrictStr] = Field(default=None, description="The logo of the customer configuration.")
    logo_dark: Optional[StrictStr] = Field(default=None, description="The dark logo of the customer configuration.", alias="logoDark")
    mail: Optional[StrictStr] = Field(default=None, description="The mail address of the customer configuration.")
    name: Optional[StrictStr] = Field(default=None, description="The name of the customer configuration.")
    www: Optional[StrictStr] = Field(default=None, description="The site web address of the customer configuration.")
    __properties: ClassVar[List[str]] = ["address", "logo", "logoDark", "mail", "name", "www"]

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
        """Create an instance of CustomerConfigDto from a JSON string"""
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
        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

        # set to None if logo (nullable) is None
        # and model_fields_set contains the field
        if self.logo is None and "logo" in self.model_fields_set:
            _dict['logo'] = None

        # set to None if logo_dark (nullable) is None
        # and model_fields_set contains the field
        if self.logo_dark is None and "logo_dark" in self.model_fields_set:
            _dict['logoDark'] = None

        # set to None if mail (nullable) is None
        # and model_fields_set contains the field
        if self.mail is None and "mail" in self.model_fields_set:
            _dict['mail'] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if www (nullable) is None
        # and model_fields_set contains the field
        if self.www is None and "www" in self.model_fields_set:
            _dict['www'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CustomerConfigDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "address": obj.get("address"),
            "logo": obj.get("logo"),
            "logoDark": obj.get("logoDark"),
            "mail": obj.get("mail"),
            "name": obj.get("name"),
            "www": obj.get("www")
        })
        return _obj


