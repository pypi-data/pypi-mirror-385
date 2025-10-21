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
from docspace_api_sdk.models.file_operation_type import FileOperationType
from typing import Optional, Set
from typing_extensions import Self

class ConversationResultDto(BaseModel):
    """
    The result of file convertion operation.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(description="The conversion operation ID.")
    operation: FileOperationType = Field(alias="Operation")
    progress: StrictInt = Field(description="The conversion operation progress.")
    source: Optional[StrictStr] = Field(default=None, description="The source file for the conversion.")
    result: Optional[Any] = Field(default=None, description="The resulting file after the conversion.")
    error: Optional[StrictStr] = Field(default=None, description="The conversion operation error message.")
    processed: Optional[StrictStr] = Field(default=None, description="Specifies if the conversion operation is processed or not.")
    __properties: ClassVar[List[str]] = ["id", "Operation", "progress", "source", "result", "error", "processed"]

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
        """Create an instance of ConversationResultDto from a JSON string"""
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
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if source (nullable) is None
        # and model_fields_set contains the field
        if self.source is None and "source" in self.model_fields_set:
            _dict['source'] = None

        # set to None if result (nullable) is None
        # and model_fields_set contains the field
        if self.result is None and "result" in self.model_fields_set:
            _dict['result'] = None

        # set to None if error (nullable) is None
        # and model_fields_set contains the field
        if self.error is None and "error" in self.model_fields_set:
            _dict['error'] = None

        # set to None if processed (nullable) is None
        # and model_fields_set contains the field
        if self.processed is None and "processed" in self.model_fields_set:
            _dict['processed'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ConversationResultDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "Operation": obj.get("Operation"),
            "progress": obj.get("progress"),
            "source": obj.get("source"),
            "result": obj.get("result"),
            "error": obj.get("error"),
            "processed": obj.get("processed")
        })
        return _obj


