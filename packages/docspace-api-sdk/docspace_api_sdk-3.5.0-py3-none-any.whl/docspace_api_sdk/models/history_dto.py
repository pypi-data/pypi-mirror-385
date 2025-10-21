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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.employee_dto import EmployeeDto
from docspace_api_sdk.models.history_action import HistoryAction
from docspace_api_sdk.models.history_data import HistoryData
from typing import Optional, Set
from typing_extensions import Self

class HistoryDto(BaseModel):
    """
    The file history information.
    """ # noqa: E501
    action: HistoryAction
    initiator: EmployeeDto
    var_date: ApiDateTime = Field(alias="date")
    data: HistoryData
    related: Optional[List[HistoryDto]] = Field(default=None, description="The list of related history.")
    __properties: ClassVar[List[str]] = ["action", "initiator", "date", "data", "related"]

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
        """Create an instance of HistoryDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of action
        if self.action:
            _dict['action'] = self.action.to_dict()
        # override the default output from pydantic by calling `to_dict()` of initiator
        if self.initiator:
            _dict['initiator'] = self.initiator.to_dict()
        # override the default output from pydantic by calling `to_dict()` of var_date
        if self.var_date:
            _dict['date'] = self.var_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of data
        if self.data:
            _dict['data'] = self.data.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in related (list)
        _items = []
        if self.related:
            for _item_related in self.related:
                if _item_related:
                    _items.append(_item_related.to_dict())
            _dict['related'] = _items
        # set to None if related (nullable) is None
        # and model_fields_set contains the field
        if self.related is None and "related" in self.model_fields_set:
            _dict['related'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of HistoryDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "action": HistoryAction.from_dict(obj["action"]) if obj.get("action") is not None else None,
            "initiator": EmployeeDto.from_dict(obj["initiator"]) if obj.get("initiator") is not None else None,
            "date": ApiDateTime.from_dict(obj["date"]) if obj.get("date") is not None else None,
            "data": HistoryData.from_dict(obj["data"]) if obj.get("data") is not None else None,
            "related": [HistoryDto.from_dict(_item) for _item in obj["related"]] if obj.get("related") is not None else None
        })
        return _obj

# TODO: Rewrite to not use raise_errors
HistoryDto.model_rebuild(raise_errors=False)

