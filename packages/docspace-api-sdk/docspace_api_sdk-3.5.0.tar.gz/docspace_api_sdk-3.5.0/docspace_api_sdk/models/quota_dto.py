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
from docspace_api_sdk.models.price_dto import PriceDto
from docspace_api_sdk.models.tenant_entity_quota_settings import TenantEntityQuotaSettings
from docspace_api_sdk.models.tenant_quota_feature_dto import TenantQuotaFeatureDto
from docspace_api_sdk.models.tenant_quota_settings import TenantQuotaSettings
from typing import Optional, Set
from typing_extensions import Self

class QuotaDto(BaseModel):
    """
    The quota information.
    """ # noqa: E501
    id: StrictInt = Field(description="The quota ID.")
    title: Optional[StrictStr] = Field(description="The quota title.")
    price: PriceDto
    non_profit: StrictBool = Field(description="Specifies if the quota is nonprofit or not.", alias="nonProfit")
    free: StrictBool = Field(description="Specifies if the quota is free or not.")
    trial: StrictBool = Field(description="Specifies if the quota is trial or not.")
    features: Optional[List[TenantQuotaFeatureDto]] = Field(description="The list of tenant quota features.")
    users_quota: Optional[TenantEntityQuotaSettings] = Field(default=None, alias="usersQuota")
    rooms_quota: Optional[TenantEntityQuotaSettings] = Field(default=None, alias="roomsQuota")
    tenant_custom_quota: Optional[TenantQuotaSettings] = Field(default=None, alias="tenantCustomQuota")
    due_date: Optional[datetime] = Field(default=None, description="The due date.", alias="dueDate")
    __properties: ClassVar[List[str]] = ["id", "title", "price", "nonProfit", "free", "trial", "features", "usersQuota", "roomsQuota", "tenantCustomQuota", "dueDate"]

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
        """Create an instance of QuotaDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of price
        if self.price:
            _dict['price'] = self.price.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in features (list)
        _items = []
        if self.features:
            for _item_features in self.features:
                if _item_features:
                    _items.append(_item_features.to_dict())
            _dict['features'] = _items
        # override the default output from pydantic by calling `to_dict()` of users_quota
        if self.users_quota:
            _dict['usersQuota'] = self.users_quota.to_dict()
        # override the default output from pydantic by calling `to_dict()` of rooms_quota
        if self.rooms_quota:
            _dict['roomsQuota'] = self.rooms_quota.to_dict()
        # override the default output from pydantic by calling `to_dict()` of tenant_custom_quota
        if self.tenant_custom_quota:
            _dict['tenantCustomQuota'] = self.tenant_custom_quota.to_dict()
        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if features (nullable) is None
        # and model_fields_set contains the field
        if self.features is None and "features" in self.model_fields_set:
            _dict['features'] = None

        # set to None if due_date (nullable) is None
        # and model_fields_set contains the field
        if self.due_date is None and "due_date" in self.model_fields_set:
            _dict['dueDate'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of QuotaDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "title": obj.get("title"),
            "price": PriceDto.from_dict(obj["price"]) if obj.get("price") is not None else None,
            "nonProfit": obj.get("nonProfit"),
            "free": obj.get("free"),
            "trial": obj.get("trial"),
            "features": [TenantQuotaFeatureDto.from_dict(_item) for _item in obj["features"]] if obj.get("features") is not None else None,
            "usersQuota": TenantEntityQuotaSettings.from_dict(obj["usersQuota"]) if obj.get("usersQuota") is not None else None,
            "roomsQuota": TenantEntityQuotaSettings.from_dict(obj["roomsQuota"]) if obj.get("roomsQuota") is not None else None,
            "tenantCustomQuota": TenantQuotaSettings.from_dict(obj["tenantCustomQuota"]) if obj.get("tenantCustomQuota") is not None else None,
            "dueDate": obj.get("dueDate")
        })
        return _obj


