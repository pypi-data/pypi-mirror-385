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

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class DraftLocationInteger(BaseModel):
    """
    The file draft parameters.
    """ # noqa: E501
    folder_id: Optional[StrictInt] = Field(default=None, description="The InProcess folder ID of the draft.", alias="folderId")
    folder_title: Optional[StrictStr] = Field(default=None, description="The InProcess folder title of the draft.", alias="folderTitle")
    file_id: Optional[StrictInt] = Field(default=None, description="The draft ID.", alias="fileId")
    file_title: Optional[StrictStr] = Field(default=None, description="The draft title.", alias="fileTitle")
    __properties: ClassVar[List[str]] = ["folderId", "folderTitle", "fileId", "fileTitle"]

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
        """Create an instance of DraftLocationInteger from a JSON string"""
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
        # set to None if folder_title (nullable) is None
        # and model_fields_set contains the field
        if self.folder_title is None and "folder_title" in self.model_fields_set:
            _dict['folderTitle'] = None

        # set to None if file_title (nullable) is None
        # and model_fields_set contains the field
        if self.file_title is None and "file_title" in self.model_fields_set:
            _dict['fileTitle'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DraftLocationInteger from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "folderId": obj.get("folderId"),
            "folderTitle": obj.get("folderTitle"),
            "fileId": obj.get("fileId"),
            "fileTitle": obj.get("fileTitle")
        })
        return _obj


