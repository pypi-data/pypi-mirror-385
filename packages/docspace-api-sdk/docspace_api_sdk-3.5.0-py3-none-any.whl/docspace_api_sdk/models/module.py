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

class Module(BaseModel):
    """
    The module information.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The module ID.")
    app_name: Optional[StrictStr] = Field(default=None, description="The module product class name.", alias="appName")
    title: Optional[StrictStr] = Field(default=None, description="The module product class name.")
    link: Optional[StrictStr] = Field(default=None, description="The URL to the module start page.")
    icon_url: Optional[StrictStr] = Field(default=None, description="The module icon URL.", alias="iconUrl")
    image_url: Optional[StrictStr] = Field(default=None, description="The module large image URL.", alias="imageUrl")
    help_url: Optional[StrictStr] = Field(default=None, description="The module help URL.", alias="helpUrl")
    description: Optional[StrictStr] = Field(default=None, description="The module description.")
    is_primary: Optional[StrictBool] = Field(default=None, description="Specifies if the module is primary or not.", alias="isPrimary")
    __properties: ClassVar[List[str]] = ["id", "appName", "title", "link", "iconUrl", "imageUrl", "helpUrl", "description", "isPrimary"]

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
        """Create an instance of Module from a JSON string"""
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
        # set to None if app_name (nullable) is None
        # and model_fields_set contains the field
        if self.app_name is None and "app_name" in self.model_fields_set:
            _dict['appName'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if link (nullable) is None
        # and model_fields_set contains the field
        if self.link is None and "link" in self.model_fields_set:
            _dict['link'] = None

        # set to None if icon_url (nullable) is None
        # and model_fields_set contains the field
        if self.icon_url is None and "icon_url" in self.model_fields_set:
            _dict['iconUrl'] = None

        # set to None if image_url (nullable) is None
        # and model_fields_set contains the field
        if self.image_url is None and "image_url" in self.model_fields_set:
            _dict['imageUrl'] = None

        # set to None if help_url (nullable) is None
        # and model_fields_set contains the field
        if self.help_url is None and "help_url" in self.model_fields_set:
            _dict['helpUrl'] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict['description'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Module from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "appName": obj.get("appName"),
            "title": obj.get("title"),
            "link": obj.get("link"),
            "iconUrl": obj.get("iconUrl"),
            "imageUrl": obj.get("imageUrl"),
            "helpUrl": obj.get("helpUrl"),
            "description": obj.get("description"),
            "isPrimary": obj.get("isPrimary")
        })
        return _obj


