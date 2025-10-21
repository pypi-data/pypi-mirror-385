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
from docspace_api_sdk.models.batch_request_dto_all_of_file_ids import BatchRequestDtoAllOfFileIds
from typing import Optional, Set
from typing_extensions import Self

class ChangeOwnerRequestDto(BaseModel):
    """
    The request parameters for changing the file owner.
    """ # noqa: E501
    folder_ids: Optional[List[BatchRequestDtoAllOfFileIds]] = Field(default=None, description="The list of folder IDs to change the owner.", alias="folderIds")
    file_ids: Optional[List[BatchRequestDtoAllOfFileIds]] = Field(default=None, description="The list of file IDs to change the owner.", alias="fileIds")
    user_id: StrictStr = Field(description="The new file owner ID.", alias="userId")
    __properties: ClassVar[List[str]] = ["folderIds", "fileIds", "userId"]

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
        """Create an instance of ChangeOwnerRequestDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in folder_ids (list)
        _items = []
        if self.folder_ids:
            for _item_folder_ids in self.folder_ids:
                if _item_folder_ids:
                    _items.append(_item_folder_ids.to_dict())
            _dict['folderIds'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in file_ids (list)
        _items = []
        if self.file_ids:
            for _item_file_ids in self.file_ids:
                if _item_file_ids:
                    _items.append(_item_file_ids.to_dict())
            _dict['fileIds'] = _items
        # set to None if folder_ids (nullable) is None
        # and model_fields_set contains the field
        if self.folder_ids is None and "folder_ids" in self.model_fields_set:
            _dict['folderIds'] = None

        # set to None if file_ids (nullable) is None
        # and model_fields_set contains the field
        if self.file_ids is None and "file_ids" in self.model_fields_set:
            _dict['fileIds'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ChangeOwnerRequestDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "folderIds": [BatchRequestDtoAllOfFileIds.from_dict(_item) for _item in obj["folderIds"]] if obj.get("folderIds") is not None else None,
            "fileIds": [BatchRequestDtoAllOfFileIds.from_dict(_item) for _item in obj["fileIds"]] if obj.get("fileIds") is not None else None,
            "userId": obj.get("userId")
        })
        return _obj


