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

class SsoIdpSettings(BaseModel):
    """
    The SSO IdP settings.
    """ # noqa: E501
    entity_id: Optional[StrictStr] = Field(default=None, description="The entity ID.", alias="entityId")
    sso_url: Optional[StrictStr] = Field(default=None, description="The SSO URL.", alias="ssoUrl")
    sso_binding: Optional[StrictStr] = Field(default=None, description="The SSO binding.", alias="ssoBinding")
    slo_url: Optional[StrictStr] = Field(default=None, description="The SLO URL.", alias="sloUrl")
    slo_binding: Optional[StrictStr] = Field(default=None, description="The SLO binding.", alias="sloBinding")
    name_id_format: Optional[StrictStr] = Field(default=None, description="The name ID format.", alias="nameIdFormat")
    __properties: ClassVar[List[str]] = ["entityId", "ssoUrl", "ssoBinding", "sloUrl", "sloBinding", "nameIdFormat"]

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
        """Create an instance of SsoIdpSettings from a JSON string"""
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
        # set to None if entity_id (nullable) is None
        # and model_fields_set contains the field
        if self.entity_id is None and "entity_id" in self.model_fields_set:
            _dict['entityId'] = None

        # set to None if sso_url (nullable) is None
        # and model_fields_set contains the field
        if self.sso_url is None and "sso_url" in self.model_fields_set:
            _dict['ssoUrl'] = None

        # set to None if sso_binding (nullable) is None
        # and model_fields_set contains the field
        if self.sso_binding is None and "sso_binding" in self.model_fields_set:
            _dict['ssoBinding'] = None

        # set to None if slo_url (nullable) is None
        # and model_fields_set contains the field
        if self.slo_url is None and "slo_url" in self.model_fields_set:
            _dict['sloUrl'] = None

        # set to None if slo_binding (nullable) is None
        # and model_fields_set contains the field
        if self.slo_binding is None and "slo_binding" in self.model_fields_set:
            _dict['sloBinding'] = None

        # set to None if name_id_format (nullable) is None
        # and model_fields_set contains the field
        if self.name_id_format is None and "name_id_format" in self.model_fields_set:
            _dict['nameIdFormat'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SsoIdpSettings from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "entityId": obj.get("entityId"),
            "ssoUrl": obj.get("ssoUrl"),
            "ssoBinding": obj.get("ssoBinding"),
            "sloUrl": obj.get("sloUrl"),
            "sloBinding": obj.get("sloBinding"),
            "nameIdFormat": obj.get("nameIdFormat")
        })
        return _obj


