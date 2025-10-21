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
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.quota import Quota
from docspace_api_sdk.models.tariff_state import TariffState
from typing import Optional, Set
from typing_extensions import Self

class Tariff(BaseModel):
    """
    The tariff parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The tariff ID.")
    state: Optional[TariffState] = None
    due_date: datetime = Field(description="The tariff due date.", alias="dueDate")
    delay_due_date: Optional[datetime] = Field(default=None, description="The tariff delay due date.", alias="delayDueDate")
    license_date: Optional[datetime] = Field(default=None, description="The tariff license date.", alias="licenseDate")
    customer_id: Optional[StrictStr] = Field(default=None, description="The tariff customer ID.", alias="customerId")
    quotas: Optional[List[Quota]] = Field(description="The list of tariff quotas.")
    overdue_quotas: Optional[List[Quota]] = Field(default=None, description="The list of overdue tariff quotas.", alias="overdueQuotas")
    __properties: ClassVar[List[str]] = ["id", "state", "dueDate", "delayDueDate", "licenseDate", "customerId", "quotas", "overdueQuotas"]

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
        """Create an instance of Tariff from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in quotas (list)
        _items = []
        if self.quotas:
            for _item_quotas in self.quotas:
                if _item_quotas:
                    _items.append(_item_quotas.to_dict())
            _dict['quotas'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in overdue_quotas (list)
        _items = []
        if self.overdue_quotas:
            for _item_overdue_quotas in self.overdue_quotas:
                if _item_overdue_quotas:
                    _items.append(_item_overdue_quotas.to_dict())
            _dict['overdueQuotas'] = _items
        # set to None if customer_id (nullable) is None
        # and model_fields_set contains the field
        if self.customer_id is None and "customer_id" in self.model_fields_set:
            _dict['customerId'] = None

        # set to None if quotas (nullable) is None
        # and model_fields_set contains the field
        if self.quotas is None and "quotas" in self.model_fields_set:
            _dict['quotas'] = None

        # set to None if overdue_quotas (nullable) is None
        # and model_fields_set contains the field
        if self.overdue_quotas is None and "overdue_quotas" in self.model_fields_set:
            _dict['overdueQuotas'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Tariff from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "state": obj.get("state"),
            "dueDate": obj.get("dueDate"),
            "delayDueDate": obj.get("delayDueDate"),
            "licenseDate": obj.get("licenseDate"),
            "customerId": obj.get("customerId"),
            "quotas": [Quota.from_dict(_item) for _item in obj["quotas"]] if obj.get("quotas") is not None else None,
            "overdueQuotas": [Quota.from_dict(_item) for _item in obj["overdueQuotas"]] if obj.get("overdueQuotas") is not None else None
        })
        return _obj


