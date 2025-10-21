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
from docspace_api_sdk.models.copy_as_json_element_dest_folder_id import CopyAsJsonElementDestFolderId
from typing import Optional, Set
from typing_extensions import Self

class CopyAsJsonElement(BaseModel):
    """
    The parameters for copying a file.
    """ # noqa: E501
    dest_title: Optional[StrictStr] = Field(description="The copied file name.", alias="destTitle")
    dest_folder_id: CopyAsJsonElementDestFolderId = Field(alias="destFolderId")
    enable_external_ext: Optional[StrictBool] = Field(default=None, description="Specifies whether to allow creating the copied file of an external extension or not.", alias="enableExternalExt")
    password: Optional[StrictStr] = Field(default=None, description="The copied file password.")
    to_form: Optional[StrictBool] = Field(default=None, description="Specifies whether to convert the file to form or not.", alias="toForm")
    __properties: ClassVar[List[str]] = ["destTitle", "destFolderId", "enableExternalExt", "password", "toForm"]

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
        """Create an instance of CopyAsJsonElement from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of dest_folder_id
        if self.dest_folder_id:
            _dict['destFolderId'] = self.dest_folder_id.to_dict()
        # set to None if dest_title (nullable) is None
        # and model_fields_set contains the field
        if self.dest_title is None and "dest_title" in self.model_fields_set:
            _dict['destTitle'] = None

        # set to None if password (nullable) is None
        # and model_fields_set contains the field
        if self.password is None and "password" in self.model_fields_set:
            _dict['password'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CopyAsJsonElement from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "destTitle": obj.get("destTitle"),
            "destFolderId": CopyAsJsonElementDestFolderId.from_dict(obj["destFolderId"]) if obj.get("destFolderId") is not None else None,
            "enableExternalExt": obj.get("enableExternalExt"),
            "password": obj.get("password"),
            "toForm": obj.get("toForm")
        })
        return _obj


