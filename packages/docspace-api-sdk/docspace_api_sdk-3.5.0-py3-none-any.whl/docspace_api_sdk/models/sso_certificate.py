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

class SsoCertificate(BaseModel):
    """
    The SSO certificate parameters.
    """ # noqa: E501
    self_signed: Optional[StrictBool] = Field(default=None, description="Specifies if a certificate is self-signed or not.", alias="selfSigned")
    crt: Optional[StrictStr] = Field(default=None, description="The CRT certificate file.")
    key: Optional[StrictStr] = Field(default=None, description="The certificate key.")
    action: Optional[StrictStr] = Field(default=None, description="The certificate action.")
    domain_name: Optional[StrictStr] = Field(default=None, description="The certificate domain name.", alias="domainName")
    start_date: Optional[datetime] = Field(default=None, description="The certificate start date.", alias="startDate")
    expired_date: Optional[datetime] = Field(default=None, description="The certificate expiration date.", alias="expiredDate")
    __properties: ClassVar[List[str]] = ["selfSigned", "crt", "key", "action", "domainName", "startDate", "expiredDate"]

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
        """Create an instance of SsoCertificate from a JSON string"""
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
        # set to None if crt (nullable) is None
        # and model_fields_set contains the field
        if self.crt is None and "crt" in self.model_fields_set:
            _dict['crt'] = None

        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if action (nullable) is None
        # and model_fields_set contains the field
        if self.action is None and "action" in self.model_fields_set:
            _dict['action'] = None

        # set to None if domain_name (nullable) is None
        # and model_fields_set contains the field
        if self.domain_name is None and "domain_name" in self.model_fields_set:
            _dict['domainName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SsoCertificate from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "selfSigned": obj.get("selfSigned"),
            "crt": obj.get("crt"),
            "key": obj.get("key"),
            "action": obj.get("action"),
            "domainName": obj.get("domainName"),
            "startDate": obj.get("startDate"),
            "expiredDate": obj.get("expiredDate")
        })
        return _obj


