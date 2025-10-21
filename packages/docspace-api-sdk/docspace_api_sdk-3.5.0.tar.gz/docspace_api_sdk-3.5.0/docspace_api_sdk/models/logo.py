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
from docspace_api_sdk.models.logo_cover import LogoCover
from typing import Optional, Set
from typing_extensions import Self

class Logo(BaseModel):
    """
    The room logo information.
    """ # noqa: E501
    original: Optional[StrictStr] = Field(description="The original logo.")
    large: Optional[StrictStr] = Field(description="The large logo.")
    medium: Optional[StrictStr] = Field(description="The medium logo.")
    small: Optional[StrictStr] = Field(description="The small logo.")
    color: Optional[StrictStr] = Field(default=None, description="The logo color.")
    cover: Optional[LogoCover] = None
    __properties: ClassVar[List[str]] = ["original", "large", "medium", "small", "color", "cover"]

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
        """Create an instance of Logo from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of cover
        if self.cover:
            _dict['cover'] = self.cover.to_dict()
        # set to None if original (nullable) is None
        # and model_fields_set contains the field
        if self.original is None and "original" in self.model_fields_set:
            _dict['original'] = None

        # set to None if large (nullable) is None
        # and model_fields_set contains the field
        if self.large is None and "large" in self.model_fields_set:
            _dict['large'] = None

        # set to None if medium (nullable) is None
        # and model_fields_set contains the field
        if self.medium is None and "medium" in self.model_fields_set:
            _dict['medium'] = None

        # set to None if small (nullable) is None
        # and model_fields_set contains the field
        if self.small is None and "small" in self.model_fields_set:
            _dict['small'] = None

        # set to None if color (nullable) is None
        # and model_fields_set contains the field
        if self.color is None and "color" in self.model_fields_set:
            _dict['color'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Logo from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "original": obj.get("original"),
            "large": obj.get("large"),
            "medium": obj.get("medium"),
            "small": obj.get("small"),
            "color": obj.get("color"),
            "cover": LogoCover.from_dict(obj["cover"]) if obj.get("cover") is not None else None
        })
        return _obj


