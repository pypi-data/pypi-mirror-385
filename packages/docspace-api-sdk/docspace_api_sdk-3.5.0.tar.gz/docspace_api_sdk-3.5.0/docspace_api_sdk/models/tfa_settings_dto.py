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

class TfaSettingsDto(BaseModel):
    """
    The parameters representing the Two-Factor Authentication (TFA) configuration settings.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(description="The ID of the TFA configuration.")
    title: Optional[StrictStr] = Field(description="The display name or description of the TFA configuration.")
    enabled: StrictBool = Field(description="Indicates whether the TFA configuration is currently active.")
    avaliable: StrictBool = Field(description="Indicates whether the TFA configuration can be used.")
    trusted_ips: Optional[List[StrictStr]] = Field(default=None, description="The list of IP addresses that are exempt from TFA requirements.", alias="trustedIps")
    mandatory_users: Optional[List[StrictStr]] = Field(default=None, description="The list of user IDs that are required to use TFA.", alias="mandatoryUsers")
    mandatory_groups: Optional[List[StrictStr]] = Field(default=None, description="The list of group IDs whose members are required to use TFA.", alias="mandatoryGroups")
    __properties: ClassVar[List[str]] = ["id", "title", "enabled", "avaliable", "trustedIps", "mandatoryUsers", "mandatoryGroups"]

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
        """Create an instance of TfaSettingsDto from a JSON string"""
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
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if trusted_ips (nullable) is None
        # and model_fields_set contains the field
        if self.trusted_ips is None and "trusted_ips" in self.model_fields_set:
            _dict['trustedIps'] = None

        # set to None if mandatory_users (nullable) is None
        # and model_fields_set contains the field
        if self.mandatory_users is None and "mandatory_users" in self.model_fields_set:
            _dict['mandatoryUsers'] = None

        # set to None if mandatory_groups (nullable) is None
        # and model_fields_set contains the field
        if self.mandatory_groups is None and "mandatory_groups" in self.model_fields_set:
            _dict['mandatoryGroups'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of TfaSettingsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "title": obj.get("title"),
            "enabled": obj.get("enabled"),
            "avaliable": obj.get("avaliable"),
            "trustedIps": obj.get("trustedIps"),
            "mandatoryUsers": obj.get("mandatoryUsers"),
            "mandatoryGroups": obj.get("mandatoryGroups")
        })
        return _obj


