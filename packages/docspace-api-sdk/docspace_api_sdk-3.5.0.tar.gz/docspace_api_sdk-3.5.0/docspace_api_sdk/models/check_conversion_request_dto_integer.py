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
from typing import Optional, Set
from typing_extensions import Self

class CheckConversionRequestDtoInteger(BaseModel):
    """
    The parameters for checking file conversion.
    """ # noqa: E501
    file_id: Optional[StrictInt] = Field(default=None, description="The file ID to check conversion proccess.", alias="fileId")
    sync: Optional[StrictBool] = Field(default=None, description="Specifies if the conversion process is synchronous or not.")
    start_convert: Optional[StrictBool] = Field(default=None, description="Specifies whether to start a conversion process or not.", alias="startConvert")
    version: Optional[StrictInt] = Field(default=None, description="The file version that is converted.")
    password: Optional[StrictStr] = Field(default=None, description="The password of the converted file.")
    output_type: Optional[StrictStr] = Field(default=None, description="The conversion output type.", alias="outputType")
    create_new_if_exist: Optional[StrictBool] = Field(default=None, description="Specifies whether to create a new file if it exists or not.", alias="createNewIfExist")
    __properties: ClassVar[List[str]] = ["fileId", "sync", "startConvert", "version", "password", "outputType", "createNewIfExist"]

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
        """Create an instance of CheckConversionRequestDtoInteger from a JSON string"""
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
        # set to None if password (nullable) is None
        # and model_fields_set contains the field
        if self.password is None and "password" in self.model_fields_set:
            _dict['password'] = None

        # set to None if output_type (nullable) is None
        # and model_fields_set contains the field
        if self.output_type is None and "output_type" in self.model_fields_set:
            _dict['outputType'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CheckConversionRequestDtoInteger from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "fileId": obj.get("fileId"),
            "sync": obj.get("sync"),
            "startConvert": obj.get("startConvert"),
            "version": obj.get("version"),
            "password": obj.get("password"),
            "outputType": obj.get("outputType"),
            "createNewIfExist": obj.get("createNewIfExist")
        })
        return _obj


