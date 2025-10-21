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

class ThumbnailsDataDto(BaseModel):
    """
    The thumbnails data parameters.
    """ # noqa: E501
    original: Optional[StrictStr] = Field(default=None, description="The thumbnail original photo.")
    retina: Optional[StrictStr] = Field(default=None, description="The thumbnail retina.")
    max: Optional[StrictStr] = Field(default=None, description="The thumbnail maximum size photo.")
    big: Optional[StrictStr] = Field(default=None, description="The thumbnail big size photo.")
    medium: Optional[StrictStr] = Field(default=None, description="The thumbnail medium size photo.")
    small: Optional[StrictStr] = Field(default=None, description="The thumbnail small size photo.")
    __properties: ClassVar[List[str]] = ["original", "retina", "max", "big", "medium", "small"]

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
        """Create an instance of ThumbnailsDataDto from a JSON string"""
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
        # set to None if original (nullable) is None
        # and model_fields_set contains the field
        if self.original is None and "original" in self.model_fields_set:
            _dict['original'] = None

        # set to None if retina (nullable) is None
        # and model_fields_set contains the field
        if self.retina is None and "retina" in self.model_fields_set:
            _dict['retina'] = None

        # set to None if max (nullable) is None
        # and model_fields_set contains the field
        if self.max is None and "max" in self.model_fields_set:
            _dict['max'] = None

        # set to None if big (nullable) is None
        # and model_fields_set contains the field
        if self.big is None and "big" in self.model_fields_set:
            _dict['big'] = None

        # set to None if medium (nullable) is None
        # and model_fields_set contains the field
        if self.medium is None and "medium" in self.model_fields_set:
            _dict['medium'] = None

        # set to None if small (nullable) is None
        # and model_fields_set contains the field
        if self.small is None and "small" in self.model_fields_set:
            _dict['small'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ThumbnailsDataDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "original": obj.get("original"),
            "retina": obj.get("retina"),
            "max": obj.get("max"),
            "big": obj.get("big"),
            "medium": obj.get("medium"),
            "small": obj.get("small")
        })
        return _obj


