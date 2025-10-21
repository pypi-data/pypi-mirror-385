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
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class TenantWalletSettings(BaseModel):
    """
    The tenant wallet settings.
    """ # noqa: E501
    enabled: Optional[StrictBool] = Field(default=None, description="Specifies whether automatic top-up for the tenant wallet is enabled.")
    min_balance: Optional[Annotated[int, Field(le=1000, strict=True, ge=5)]] = Field(default=None, description="The minimum wallet balance at which automatic top-up will be triggered. Must be between 5 and 1000.", alias="minBalance")
    up_to_balance: Optional[Annotated[int, Field(le=5000, strict=True, ge=6)]] = Field(default=None, description="The maximum wallet balance at which automatic top-up will be triggered. Must be between 6 and 5000.", alias="upToBalance")
    currency: Optional[StrictStr] = Field(default=None, description="The three-character ISO 4217 currency symbol.")
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the tenant wallet settings were last modified.", alias="lastModified")
    __properties: ClassVar[List[str]] = ["enabled", "minBalance", "upToBalance", "currency", "lastModified"]

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
        """Create an instance of TenantWalletSettings from a JSON string"""
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
        # set to None if currency (nullable) is None
        # and model_fields_set contains the field
        if self.currency is None and "currency" in self.model_fields_set:
            _dict['currency'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of TenantWalletSettings from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "enabled": obj.get("enabled"),
            "minBalance": obj.get("minBalance"),
            "upToBalance": obj.get("upToBalance"),
            "currency": obj.get("currency"),
            "lastModified": obj.get("lastModified")
        })
        return _obj


