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

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from docspace_api_sdk.models.room_data_lifetime_period import RoomDataLifetimePeriod
from typing import Optional, Set
from typing_extensions import Self

class RoomDataLifetimeDto(BaseModel):
    """
    The room data lifetime information.
    """ # noqa: E501
    delete_permanently: StrictBool = Field(description="Specifies whether to permanently delete the room data or not.", alias="deletePermanently")
    period: RoomDataLifetimePeriod
    value: Optional[Annotated[int, Field(le=999, strict=True, ge=1)]] = Field(default=None, description="Specifies the time period value of the room data lifetime.")
    enabled: Optional[StrictBool] = Field(default=None, description="Specifies whether the room data lifetime setting is enabled or not.")
    __properties: ClassVar[List[str]] = ["deletePermanently", "period", "value", "enabled"]

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
        """Create an instance of RoomDataLifetimeDto from a JSON string"""
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
        # set to None if value (nullable) is None
        # and model_fields_set contains the field
        if self.value is None and "value" in self.model_fields_set:
            _dict['value'] = None

        # set to None if enabled (nullable) is None
        # and model_fields_set contains the field
        if self.enabled is None and "enabled" in self.model_fields_set:
            _dict['enabled'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of RoomDataLifetimeDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "deletePermanently": obj.get("deletePermanently"),
            "period": obj.get("period"),
            "value": obj.get("value"),
            "enabled": obj.get("enabled")
        })
        return _obj


