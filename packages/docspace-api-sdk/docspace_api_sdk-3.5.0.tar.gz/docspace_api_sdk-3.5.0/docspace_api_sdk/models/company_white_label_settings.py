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
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class CompanyWhiteLabelSettings(BaseModel):
    """
    The company white label settings.
    """ # noqa: E501
    company_name: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The company name.", alias="companyName")
    site: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The company site.")
    email: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The company email address.")
    address: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The company address.")
    phone: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The company phone number.")
    is_licensor: Optional[StrictBool] = Field(default=None, description="Specifies if a company is a licensor or not.", alias="IsLicensor")
    hide_about: Optional[StrictBool] = Field(default=None, description="Specifies if the About page is visible or not", alias="hideAbout")
    last_modified: Optional[datetime] = Field(default=None, alias="lastModified")
    __properties: ClassVar[List[str]] = ["companyName", "site", "email", "address", "phone", "IsLicensor", "hideAbout", "lastModified"]

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
        """Create an instance of CompanyWhiteLabelSettings from a JSON string"""
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
        # set to None if company_name (nullable) is None
        # and model_fields_set contains the field
        if self.company_name is None and "company_name" in self.model_fields_set:
            _dict['companyName'] = None

        # set to None if site (nullable) is None
        # and model_fields_set contains the field
        if self.site is None and "site" in self.model_fields_set:
            _dict['site'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if address (nullable) is None
        # and model_fields_set contains the field
        if self.address is None and "address" in self.model_fields_set:
            _dict['address'] = None

        # set to None if phone (nullable) is None
        # and model_fields_set contains the field
        if self.phone is None and "phone" in self.model_fields_set:
            _dict['phone'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CompanyWhiteLabelSettings from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "companyName": obj.get("companyName"),
            "site": obj.get("site"),
            "email": obj.get("email"),
            "address": obj.get("address"),
            "phone": obj.get("phone"),
            "IsLicensor": obj.get("IsLicensor"),
            "hideAbout": obj.get("hideAbout"),
            "lastModified": obj.get("lastModified")
        })
        return _obj


