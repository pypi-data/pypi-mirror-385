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
from docspace_api_sdk.models.co_editing_config import CoEditingConfig
from docspace_api_sdk.models.customization_config_dto import CustomizationConfigDto
from docspace_api_sdk.models.embedded_config import EmbeddedConfig
from docspace_api_sdk.models.encryption_keys_config import EncryptionKeysConfig
from docspace_api_sdk.models.plugins_config import PluginsConfig
from docspace_api_sdk.models.recent_config import RecentConfig
from docspace_api_sdk.models.templates_config import TemplatesConfig
from docspace_api_sdk.models.user_config import UserConfig
from typing import Optional, Set
from typing_extensions import Self

class EditorConfigurationDto(BaseModel):
    """
    The editor configuration parameters.
    """ # noqa: E501
    callback_url: Optional[StrictStr] = Field(default=None, description="The callback URL of the editor.", alias="callbackUrl")
    co_editing: Optional[CoEditingConfig] = Field(default=None, alias="coEditing")
    create_url: Optional[StrictStr] = Field(default=None, description="The creation URL of the editor.", alias="createUrl")
    customization: Optional[CustomizationConfigDto] = None
    embedded: Optional[EmbeddedConfig] = None
    encryption_keys: Optional[EncryptionKeysConfig] = Field(default=None, alias="encryptionKeys")
    lang: Optional[StrictStr] = Field(description="The language of the editor configuration.")
    mode: Optional[StrictStr] = Field(description="The mode of the editor configuration.")
    mode_write: Optional[StrictBool] = Field(default=None, description="Specifies if the mode is write of the editor configuration.", alias="modeWrite")
    plugins: Optional[PluginsConfig] = None
    recent: Optional[List[RecentConfig]] = Field(default=None, description="The recent configuration of the editor.")
    templates: Optional[List[TemplatesConfig]] = Field(default=None, description="The templates of the editor configuration.")
    user: UserConfig
    __properties: ClassVar[List[str]] = ["callbackUrl", "coEditing", "createUrl", "customization", "embedded", "encryptionKeys", "lang", "mode", "modeWrite", "plugins", "recent", "templates", "user"]

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
        """Create an instance of EditorConfigurationDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of co_editing
        if self.co_editing:
            _dict['coEditing'] = self.co_editing.to_dict()
        # override the default output from pydantic by calling `to_dict()` of customization
        if self.customization:
            _dict['customization'] = self.customization.to_dict()
        # override the default output from pydantic by calling `to_dict()` of embedded
        if self.embedded:
            _dict['embedded'] = self.embedded.to_dict()
        # override the default output from pydantic by calling `to_dict()` of encryption_keys
        if self.encryption_keys:
            _dict['encryptionKeys'] = self.encryption_keys.to_dict()
        # override the default output from pydantic by calling `to_dict()` of plugins
        if self.plugins:
            _dict['plugins'] = self.plugins.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in recent (list)
        _items = []
        if self.recent:
            for _item_recent in self.recent:
                if _item_recent:
                    _items.append(_item_recent.to_dict())
            _dict['recent'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in templates (list)
        _items = []
        if self.templates:
            for _item_templates in self.templates:
                if _item_templates:
                    _items.append(_item_templates.to_dict())
            _dict['templates'] = _items
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        # set to None if callback_url (nullable) is None
        # and model_fields_set contains the field
        if self.callback_url is None and "callback_url" in self.model_fields_set:
            _dict['callbackUrl'] = None

        # set to None if create_url (nullable) is None
        # and model_fields_set contains the field
        if self.create_url is None and "create_url" in self.model_fields_set:
            _dict['createUrl'] = None

        # set to None if lang (nullable) is None
        # and model_fields_set contains the field
        if self.lang is None and "lang" in self.model_fields_set:
            _dict['lang'] = None

        # set to None if mode (nullable) is None
        # and model_fields_set contains the field
        if self.mode is None and "mode" in self.model_fields_set:
            _dict['mode'] = None

        # set to None if recent (nullable) is None
        # and model_fields_set contains the field
        if self.recent is None and "recent" in self.model_fields_set:
            _dict['recent'] = None

        # set to None if templates (nullable) is None
        # and model_fields_set contains the field
        if self.templates is None and "templates" in self.model_fields_set:
            _dict['templates'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EditorConfigurationDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "callbackUrl": obj.get("callbackUrl"),
            "coEditing": CoEditingConfig.from_dict(obj["coEditing"]) if obj.get("coEditing") is not None else None,
            "createUrl": obj.get("createUrl"),
            "customization": CustomizationConfigDto.from_dict(obj["customization"]) if obj.get("customization") is not None else None,
            "embedded": EmbeddedConfig.from_dict(obj["embedded"]) if obj.get("embedded") is not None else None,
            "encryptionKeys": EncryptionKeysConfig.from_dict(obj["encryptionKeys"]) if obj.get("encryptionKeys") is not None else None,
            "lang": obj.get("lang"),
            "mode": obj.get("mode"),
            "modeWrite": obj.get("modeWrite"),
            "plugins": PluginsConfig.from_dict(obj["plugins"]) if obj.get("plugins") is not None else None,
            "recent": [RecentConfig.from_dict(_item) for _item in obj["recent"]] if obj.get("recent") is not None else None,
            "templates": [TemplatesConfig.from_dict(_item) for _item in obj["templates"]] if obj.get("templates") is not None else None,
            "user": UserConfig.from_dict(obj["user"]) if obj.get("user") is not None else None
        })
        return _obj


