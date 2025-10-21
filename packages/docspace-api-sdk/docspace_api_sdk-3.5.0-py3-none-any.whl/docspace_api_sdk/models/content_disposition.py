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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class ContentDisposition(BaseModel):
    """
    ContentDisposition
    """ # noqa: E501
    disposition_type: Optional[StrictStr] = Field(default=None, alias="dispositionType")
    parameters: Optional[List[Any]] = None
    file_name: Optional[StrictStr] = Field(default=None, alias="fileName")
    creation_date: Optional[datetime] = Field(default=None, alias="creationDate")
    modification_date: Optional[datetime] = Field(default=None, alias="modificationDate")
    inline: Optional[StrictBool] = None
    read_date: Optional[datetime] = Field(default=None, alias="readDate")
    size: Optional[StrictInt] = None
    __properties: ClassVar[List[str]] = ["dispositionType", "parameters", "fileName", "creationDate", "modificationDate", "inline", "readDate", "size"]

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
        """Create an instance of ContentDisposition from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "parameters",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if disposition_type (nullable) is None
        # and model_fields_set contains the field
        if self.disposition_type is None and "disposition_type" in self.model_fields_set:
            _dict['dispositionType'] = None

        # set to None if parameters (nullable) is None
        # and model_fields_set contains the field
        if self.parameters is None and "parameters" in self.model_fields_set:
            _dict['parameters'] = None

        # set to None if file_name (nullable) is None
        # and model_fields_set contains the field
        if self.file_name is None and "file_name" in self.model_fields_set:
            _dict['fileName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ContentDisposition from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "dispositionType": obj.get("dispositionType"),
            "parameters": obj.get("parameters"),
            "fileName": obj.get("fileName"),
            "creationDate": obj.get("creationDate"),
            "modificationDate": obj.get("modificationDate"),
            "inline": obj.get("inline"),
            "readDate": obj.get("readDate"),
            "size": obj.get("size")
        })
        return _obj


