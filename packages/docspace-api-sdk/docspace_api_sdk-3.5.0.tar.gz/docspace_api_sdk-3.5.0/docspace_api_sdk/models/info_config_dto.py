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
from docspace_api_sdk.models.ace_short_wrapper import AceShortWrapper
from docspace_api_sdk.models.editor_type import EditorType
from typing import Optional, Set
from typing_extensions import Self

class InfoConfigDto(BaseModel):
    """
    The information config parameters.
    """ # noqa: E501
    favorite: Optional[StrictBool] = Field(default=None, description="Specifies if the file is favorite or not.")
    folder: Optional[StrictStr] = Field(default=None, description="The folder of the file.")
    owner: Optional[StrictStr] = Field(default=None, description="The file owner.")
    sharing_settings: Optional[List[AceShortWrapper]] = Field(default=None, description="The sharing settings of the file.", alias="sharingSettings")
    type: Optional[EditorType] = None
    uploaded: Optional[StrictStr] = Field(default=None, description="The uploaded file.")
    __properties: ClassVar[List[str]] = ["favorite", "folder", "owner", "sharingSettings", "type", "uploaded"]

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
        """Create an instance of InfoConfigDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in sharing_settings (list)
        _items = []
        if self.sharing_settings:
            for _item_sharing_settings in self.sharing_settings:
                if _item_sharing_settings:
                    _items.append(_item_sharing_settings.to_dict())
            _dict['sharingSettings'] = _items
        # set to None if favorite (nullable) is None
        # and model_fields_set contains the field
        if self.favorite is None and "favorite" in self.model_fields_set:
            _dict['favorite'] = None

        # set to None if folder (nullable) is None
        # and model_fields_set contains the field
        if self.folder is None and "folder" in self.model_fields_set:
            _dict['folder'] = None

        # set to None if owner (nullable) is None
        # and model_fields_set contains the field
        if self.owner is None and "owner" in self.model_fields_set:
            _dict['owner'] = None

        # set to None if sharing_settings (nullable) is None
        # and model_fields_set contains the field
        if self.sharing_settings is None and "sharing_settings" in self.model_fields_set:
            _dict['sharingSettings'] = None

        # set to None if uploaded (nullable) is None
        # and model_fields_set contains the field
        if self.uploaded is None and "uploaded" in self.model_fields_set:
            _dict['uploaded'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of InfoConfigDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "favorite": obj.get("favorite"),
            "folder": obj.get("folder"),
            "owner": obj.get("owner"),
            "sharingSettings": [AceShortWrapper.from_dict(_item) for _item in obj["sharingSettings"]] if obj.get("sharingSettings") is not None else None,
            "type": obj.get("type"),
            "uploaded": obj.get("uploaded")
        })
        return _obj


