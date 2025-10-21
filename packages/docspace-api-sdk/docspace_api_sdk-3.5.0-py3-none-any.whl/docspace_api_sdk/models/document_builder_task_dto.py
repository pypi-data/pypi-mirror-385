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
from docspace_api_sdk.models.distributed_task_status import DistributedTaskStatus
from typing import Optional, Set
from typing_extensions import Self

class DocumentBuilderTaskDto(BaseModel):
    """
    The Document Builder task parameters.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(description="The Document Builder task ID.")
    error: Optional[StrictStr] = Field(description="The error message occurred during the document building process.")
    percentage: StrictInt = Field(description="The progress percentage of the document building process.")
    is_completed: StrictBool = Field(description="Specifies whether the document building process is completed or not.", alias="isCompleted")
    status: DistributedTaskStatus
    result_file_id: Optional[Any] = Field(description="The result file ID.", alias="resultFileId")
    result_file_name: Optional[StrictStr] = Field(description="The result file name.", alias="resultFileName")
    result_file_url: Optional[StrictStr] = Field(description="The result file URL.", alias="resultFileUrl")
    __properties: ClassVar[List[str]] = ["id", "error", "percentage", "isCompleted", "status", "resultFileId", "resultFileName", "resultFileUrl"]

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
        """Create an instance of DocumentBuilderTaskDto from a JSON string"""
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

        # set to None if error (nullable) is None
        # and model_fields_set contains the field
        if self.error is None and "error" in self.model_fields_set:
            _dict['error'] = None

        # set to None if result_file_id (nullable) is None
        # and model_fields_set contains the field
        if self.result_file_id is None and "result_file_id" in self.model_fields_set:
            _dict['resultFileId'] = None

        # set to None if result_file_name (nullable) is None
        # and model_fields_set contains the field
        if self.result_file_name is None and "result_file_name" in self.model_fields_set:
            _dict['resultFileName'] = None

        # set to None if result_file_url (nullable) is None
        # and model_fields_set contains the field
        if self.result_file_url is None and "result_file_url" in self.model_fields_set:
            _dict['resultFileUrl'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DocumentBuilderTaskDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "error": obj.get("error"),
            "percentage": obj.get("percentage"),
            "isCompleted": obj.get("isCompleted"),
            "status": obj.get("status"),
            "resultFileId": obj.get("resultFileId"),
            "resultFileName": obj.get("resultFileName"),
            "resultFileUrl": obj.get("resultFileUrl")
        })
        return _obj


