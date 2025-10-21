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
from docspace_api_sdk.models.employee_dto import EmployeeDto
from typing import Optional, Set
from typing_extensions import Self

class WebPluginDto(BaseModel):
    """
    The web plugin information.
    """ # noqa: E501
    name: Optional[StrictStr] = Field(description="The web plugin name.")
    version: Optional[StrictStr] = Field(description="The web plugin version.")
    min_doc_space_version: Optional[StrictStr] = Field(default=None, description="The minimum version of DocSpace with which the plugin is guaranteed to work.", alias="minDocSpaceVersion")
    description: Optional[StrictStr] = Field(description="The web plugin description.")
    license: Optional[StrictStr] = Field(description="The web plugin license.")
    author: Optional[StrictStr] = Field(description="The web plugin author.")
    home_page: Optional[StrictStr] = Field(description="The web plugin home page URL.", alias="homePage")
    plugin_name: Optional[StrictStr] = Field(description="The name by which the web plugin is registered in the window object.", alias="pluginName")
    scopes: Optional[StrictStr] = Field(description="The web plugin scopes.")
    image: Optional[StrictStr] = Field(description="The web plugin image.")
    create_by: EmployeeDto = Field(alias="createBy")
    create_on: datetime = Field(description="The date and time when the web plugin was created.", alias="createOn")
    enabled: StrictBool = Field(description="Specifies if the web plugin is enabled or not.")
    system: StrictBool = Field(description="Specifies if the web plugin is system or not.")
    url: Optional[StrictStr] = Field(description="The web plugin URL.")
    settings: Optional[StrictStr] = Field(description="The web plugin settings.")
    __properties: ClassVar[List[str]] = ["name", "version", "minDocSpaceVersion", "description", "license", "author", "homePage", "pluginName", "scopes", "image", "createBy", "createOn", "enabled", "system", "url", "settings"]

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
        """Create an instance of WebPluginDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of create_by
        if self.create_by:
            _dict['createBy'] = self.create_by.to_dict()
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if version (nullable) is None
        # and model_fields_set contains the field
        if self.version is None and "version" in self.model_fields_set:
            _dict['version'] = None

        # set to None if min_doc_space_version (nullable) is None
        # and model_fields_set contains the field
        if self.min_doc_space_version is None and "min_doc_space_version" in self.model_fields_set:
            _dict['minDocSpaceVersion'] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict['description'] = None

        # set to None if license (nullable) is None
        # and model_fields_set contains the field
        if self.license is None and "license" in self.model_fields_set:
            _dict['license'] = None

        # set to None if author (nullable) is None
        # and model_fields_set contains the field
        if self.author is None and "author" in self.model_fields_set:
            _dict['author'] = None

        # set to None if home_page (nullable) is None
        # and model_fields_set contains the field
        if self.home_page is None and "home_page" in self.model_fields_set:
            _dict['homePage'] = None

        # set to None if plugin_name (nullable) is None
        # and model_fields_set contains the field
        if self.plugin_name is None and "plugin_name" in self.model_fields_set:
            _dict['pluginName'] = None

        # set to None if scopes (nullable) is None
        # and model_fields_set contains the field
        if self.scopes is None and "scopes" in self.model_fields_set:
            _dict['scopes'] = None

        # set to None if image (nullable) is None
        # and model_fields_set contains the field
        if self.image is None and "image" in self.model_fields_set:
            _dict['image'] = None

        # set to None if url (nullable) is None
        # and model_fields_set contains the field
        if self.url is None and "url" in self.model_fields_set:
            _dict['url'] = None

        # set to None if settings (nullable) is None
        # and model_fields_set contains the field
        if self.settings is None and "settings" in self.model_fields_set:
            _dict['settings'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WebPluginDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "version": obj.get("version"),
            "minDocSpaceVersion": obj.get("minDocSpaceVersion"),
            "description": obj.get("description"),
            "license": obj.get("license"),
            "author": obj.get("author"),
            "homePage": obj.get("homePage"),
            "pluginName": obj.get("pluginName"),
            "scopes": obj.get("scopes"),
            "image": obj.get("image"),
            "createBy": EmployeeDto.from_dict(obj["createBy"]) if obj.get("createBy") is not None else None,
            "createOn": obj.get("createOn"),
            "enabled": obj.get("enabled"),
            "system": obj.get("system"),
            "url": obj.get("url"),
            "settings": obj.get("settings")
        })
        return _obj


