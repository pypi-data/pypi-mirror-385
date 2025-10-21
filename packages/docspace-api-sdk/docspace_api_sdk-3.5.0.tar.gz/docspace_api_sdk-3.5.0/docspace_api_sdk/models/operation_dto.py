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

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from docspace_api_sdk.models.api_date_time import ApiDateTime
from typing import Optional, Set
from typing_extensions import Self

class OperationDto(BaseModel):
    """
    Represents an operation.
    """ # noqa: E501
    var_date: Optional[ApiDateTime] = Field(default=None, alias="date")
    service: Optional[StrictStr] = Field(default=None, description="The service related to the operation.")
    description: Optional[StrictStr] = Field(default=None, description="The brief operation description.")
    details: Optional[StrictStr] = Field(default=None, description="The detailed information about the operation.")
    service_unit: Optional[StrictStr] = Field(default=None, description="The service unit.", alias="serviceUnit")
    quantity: Optional[StrictInt] = Field(default=None, description="The quantity of the service used.")
    currency: Optional[StrictStr] = Field(default=None, description="The three-character ISO 4217 currency symbol of the operation.")
    credit: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The credit amount of the operation.")
    debit: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The debit amount of the operation.")
    participant_name: Optional[StrictStr] = Field(default=None, description="The participant original name.", alias="participantName")
    participant_display_name: Optional[StrictStr] = Field(default=None, description="The participant display name.", alias="participantDisplayName")
    __properties: ClassVar[List[str]] = ["date", "service", "description", "details", "serviceUnit", "quantity", "currency", "credit", "debit", "participantName", "participantDisplayName"]

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
        """Create an instance of OperationDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of var_date
        if self.var_date:
            _dict['date'] = self.var_date.to_dict()
        # set to None if service (nullable) is None
        # and model_fields_set contains the field
        if self.service is None and "service" in self.model_fields_set:
            _dict['service'] = None

        # set to None if description (nullable) is None
        # and model_fields_set contains the field
        if self.description is None and "description" in self.model_fields_set:
            _dict['description'] = None

        # set to None if details (nullable) is None
        # and model_fields_set contains the field
        if self.details is None and "details" in self.model_fields_set:
            _dict['details'] = None

        # set to None if service_unit (nullable) is None
        # and model_fields_set contains the field
        if self.service_unit is None and "service_unit" in self.model_fields_set:
            _dict['serviceUnit'] = None

        # set to None if currency (nullable) is None
        # and model_fields_set contains the field
        if self.currency is None and "currency" in self.model_fields_set:
            _dict['currency'] = None

        # set to None if participant_name (nullable) is None
        # and model_fields_set contains the field
        if self.participant_name is None and "participant_name" in self.model_fields_set:
            _dict['participantName'] = None

        # set to None if participant_display_name (nullable) is None
        # and model_fields_set contains the field
        if self.participant_display_name is None and "participant_display_name" in self.model_fields_set:
            _dict['participantDisplayName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of OperationDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "date": ApiDateTime.from_dict(obj["date"]) if obj.get("date") is not None else None,
            "service": obj.get("service"),
            "description": obj.get("description"),
            "details": obj.get("details"),
            "serviceUnit": obj.get("serviceUnit"),
            "quantity": obj.get("quantity"),
            "currency": obj.get("currency"),
            "credit": obj.get("credit"),
            "debit": obj.get("debit"),
            "participantName": obj.get("participantName"),
            "participantDisplayName": obj.get("participantDisplayName")
        })
        return _obj


