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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.file_entry_base_dto import FileEntryBaseDto
from docspace_api_sdk.models.file_operation_type import FileOperationType
from typing import Optional, Set
from typing_extensions import Self

class FileOperationDto(BaseModel):
    """
    The file operation information.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(description="The file operation ID.")
    operation: FileOperationType = Field(alias="Operation")
    progress: StrictInt = Field(description="The file operation progress in percentage.")
    error: Optional[StrictStr] = Field(description="The file operation error message.")
    processed: Optional[StrictStr] = Field(description="The file operation processing status.")
    finished: StrictBool = Field(description="Specifies if the file operation is finished or not.")
    url: Optional[StrictStr] = Field(default=None, description="The file operation URL.")
    files: Optional[List[FileEntryBaseDto]] = Field(default=None, description="The list of files of the file operation.")
    folders: Optional[List[FileEntryBaseDto]] = Field(default=None, description="The list of folders of the file operation.")
    __properties: ClassVar[List[str]] = ["id", "Operation", "progress", "error", "processed", "finished", "url", "files", "folders"]

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
        """Create an instance of FileOperationDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in files (list)
        _items = []
        if self.files:
            for _item_files in self.files:
                if _item_files:
                    _items.append(_item_files.to_dict())
            _dict['files'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in folders (list)
        _items = []
        if self.folders:
            for _item_folders in self.folders:
                if _item_folders:
                    _items.append(_item_folders.to_dict())
            _dict['folders'] = _items
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if error (nullable) is None
        # and model_fields_set contains the field
        if self.error is None and "error" in self.model_fields_set:
            _dict['error'] = None

        # set to None if processed (nullable) is None
        # and model_fields_set contains the field
        if self.processed is None and "processed" in self.model_fields_set:
            _dict['processed'] = None

        # set to None if url (nullable) is None
        # and model_fields_set contains the field
        if self.url is None and "url" in self.model_fields_set:
            _dict['url'] = None

        # set to None if files (nullable) is None
        # and model_fields_set contains the field
        if self.files is None and "files" in self.model_fields_set:
            _dict['files'] = None

        # set to None if folders (nullable) is None
        # and model_fields_set contains the field
        if self.folders is None and "folders" in self.model_fields_set:
            _dict['folders'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FileOperationDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "Operation": obj.get("Operation"),
            "progress": obj.get("progress"),
            "error": obj.get("error"),
            "processed": obj.get("processed"),
            "finished": obj.get("finished"),
            "url": obj.get("url"),
            "files": [FileEntryBaseDto.from_dict(_item) for _item in obj["files"]] if obj.get("files") is not None else None,
            "folders": [FileEntryBaseDto.from_dict(_item) for _item in obj["folders"]] if obj.get("folders") is not None else None
        })
        return _obj


