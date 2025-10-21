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
from docspace_api_sdk.models.api_date_time import ApiDateTime
from typing import Optional, Set
from typing_extensions import Self

class SessionRequest(BaseModel):
    """
    The session request parameters.
    """ # noqa: E501
    file_name: Optional[StrictStr] = Field(description="The file name.", alias="fileName")
    file_size: Optional[StrictInt] = Field(default=None, description="The file size.", alias="fileSize")
    relative_path: Optional[StrictStr] = Field(default=None, description="The relative path to the file.", alias="relativePath")
    create_on: Optional[ApiDateTime] = Field(default=None, alias="createOn")
    encrypted: Optional[StrictBool] = Field(default=None, description="Specifies whether the file is encrypted or not.")
    create_new_if_exist: Optional[StrictBool] = Field(default=None, description="Specifies whether to create a new file if it already exists.", alias="createNewIfExist")
    __properties: ClassVar[List[str]] = ["fileName", "fileSize", "relativePath", "createOn", "encrypted", "createNewIfExist"]

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
        """Create an instance of SessionRequest from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of create_on
        if self.create_on:
            _dict['createOn'] = self.create_on.to_dict()
        # set to None if file_name (nullable) is None
        # and model_fields_set contains the field
        if self.file_name is None and "file_name" in self.model_fields_set:
            _dict['fileName'] = None

        # set to None if relative_path (nullable) is None
        # and model_fields_set contains the field
        if self.relative_path is None and "relative_path" in self.model_fields_set:
            _dict['relativePath'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SessionRequest from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "fileName": obj.get("fileName"),
            "fileSize": obj.get("fileSize"),
            "relativePath": obj.get("relativePath"),
            "createOn": ApiDateTime.from_dict(obj["createOn"]) if obj.get("createOn") is not None else None,
            "encrypted": obj.get("encrypted"),
            "createNewIfExist": obj.get("createNewIfExist")
        })
        return _obj


