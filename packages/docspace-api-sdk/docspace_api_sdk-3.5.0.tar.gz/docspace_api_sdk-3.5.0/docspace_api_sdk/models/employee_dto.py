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

class EmployeeDto(BaseModel):
    """
    The user parameters.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The user ID.")
    display_name: Optional[StrictStr] = Field(default=None, description="The user display name.", alias="displayName")
    title: Optional[StrictStr] = Field(default=None, description="The user title.")
    avatar: Optional[StrictStr] = Field(default=None, description="The user avatar.")
    avatar_original: Optional[StrictStr] = Field(default=None, description="The user original size avatar.", alias="avatarOriginal")
    avatar_max: Optional[StrictStr] = Field(default=None, description="The user maximum size avatar.", alias="avatarMax")
    avatar_medium: Optional[StrictStr] = Field(default=None, description="The user medium size avatar.", alias="avatarMedium")
    avatar_small: Optional[StrictStr] = Field(default=None, description="The user small size avatar.", alias="avatarSmall")
    profile_url: Optional[StrictStr] = Field(default=None, description="The user profile URL.", alias="profileUrl")
    has_avatar: Optional[StrictBool] = Field(default=None, description="Specifies if the user has an avatar or not.", alias="hasAvatar")
    is_anonim: Optional[StrictBool] = Field(default=None, description="Specifies if the user is anonymous or not.", alias="isAnonim")
    __properties: ClassVar[List[str]] = ["id", "displayName", "title", "avatar", "avatarOriginal", "avatarMax", "avatarMedium", "avatarSmall", "profileUrl", "hasAvatar", "isAnonim"]

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
        """Create an instance of EmployeeDto from a JSON string"""
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
        # set to None if display_name (nullable) is None
        # and model_fields_set contains the field
        if self.display_name is None and "display_name" in self.model_fields_set:
            _dict['displayName'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if avatar (nullable) is None
        # and model_fields_set contains the field
        if self.avatar is None and "avatar" in self.model_fields_set:
            _dict['avatar'] = None

        # set to None if avatar_original (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_original is None and "avatar_original" in self.model_fields_set:
            _dict['avatarOriginal'] = None

        # set to None if avatar_max (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_max is None and "avatar_max" in self.model_fields_set:
            _dict['avatarMax'] = None

        # set to None if avatar_medium (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_medium is None and "avatar_medium" in self.model_fields_set:
            _dict['avatarMedium'] = None

        # set to None if avatar_small (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_small is None and "avatar_small" in self.model_fields_set:
            _dict['avatarSmall'] = None

        # set to None if profile_url (nullable) is None
        # and model_fields_set contains the field
        if self.profile_url is None and "profile_url" in self.model_fields_set:
            _dict['profileUrl'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EmployeeDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "displayName": obj.get("displayName"),
            "title": obj.get("title"),
            "avatar": obj.get("avatar"),
            "avatarOriginal": obj.get("avatarOriginal"),
            "avatarMax": obj.get("avatarMax"),
            "avatarMedium": obj.get("avatarMedium"),
            "avatarSmall": obj.get("avatarSmall"),
            "profileUrl": obj.get("profileUrl"),
            "hasAvatar": obj.get("hasAvatar"),
            "isAnonim": obj.get("isAnonim")
        })
        return _obj


