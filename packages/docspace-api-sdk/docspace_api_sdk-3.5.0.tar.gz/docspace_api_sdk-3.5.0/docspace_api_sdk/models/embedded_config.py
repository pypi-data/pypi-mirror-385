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

class EmbeddedConfig(BaseModel):
    """
    The configuration parameters for the embedded document type.
    """ # noqa: E501
    embed_url: Optional[StrictStr] = Field(default=None, description="The absolute URL to the document serving as a source file for the document embedded into the web page.", alias="embedUrl")
    save_url: Optional[StrictStr] = Field(default=None, description="The absolute URL that will allow the document to be saved onto the user personal computer.", alias="saveUrl")
    share_link_param: Optional[StrictStr] = Field(default=None, description="The shared URL parameter.", alias="shareLinkParam")
    share_url: Optional[StrictStr] = Field(default=None, description="The absolute URL that will allow other users to share this document.", alias="shareUrl")
    toolbar_docked: Optional[StrictStr] = Field(default=None, description="The place for the embedded viewer toolbar, can be either top or bottom.", alias="toolbarDocked")
    __properties: ClassVar[List[str]] = ["embedUrl", "saveUrl", "shareLinkParam", "shareUrl", "toolbarDocked"]

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
        """Create an instance of EmbeddedConfig from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "save_url",
            "toolbar_docked",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if embed_url (nullable) is None
        # and model_fields_set contains the field
        if self.embed_url is None and "embed_url" in self.model_fields_set:
            _dict['embedUrl'] = None

        # set to None if save_url (nullable) is None
        # and model_fields_set contains the field
        if self.save_url is None and "save_url" in self.model_fields_set:
            _dict['saveUrl'] = None

        # set to None if share_link_param (nullable) is None
        # and model_fields_set contains the field
        if self.share_link_param is None and "share_link_param" in self.model_fields_set:
            _dict['shareLinkParam'] = None

        # set to None if share_url (nullable) is None
        # and model_fields_set contains the field
        if self.share_url is None and "share_url" in self.model_fields_set:
            _dict['shareUrl'] = None

        # set to None if toolbar_docked (nullable) is None
        # and model_fields_set contains the field
        if self.toolbar_docked is None and "toolbar_docked" in self.model_fields_set:
            _dict['toolbarDocked'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EmbeddedConfig from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "embedUrl": obj.get("embedUrl"),
            "saveUrl": obj.get("saveUrl"),
            "shareLinkParam": obj.get("shareLinkParam"),
            "shareUrl": obj.get("shareUrl"),
            "toolbarDocked": obj.get("toolbarDocked")
        })
        return _obj


