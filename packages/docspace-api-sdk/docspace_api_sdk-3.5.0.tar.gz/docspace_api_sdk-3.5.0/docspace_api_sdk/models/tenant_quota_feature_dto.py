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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.feature_used_dto import FeatureUsedDto
from typing import Optional, Set
from typing_extensions import Self

class TenantQuotaFeatureDto(BaseModel):
    """
    The tenant quota feature parameters.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The ID of the tenant quota feature.")
    title: Optional[StrictStr] = Field(default=None, description="The title of the tenant quota feature.")
    image: Optional[StrictStr] = Field(default=None, description="The image URL of the tenant quota feature.")
    value: Optional[Any] = Field(default=None, description="The value of the tenant quota feature.")
    type: Optional[StrictStr] = Field(default=None, description="The type of the tenant quota feature.")
    used: Optional[FeatureUsedDto] = None
    price_title: Optional[StrictStr] = Field(default=None, description="The price title of the tenant quota feature.", alias="priceTitle")
    __properties: ClassVar[List[str]] = ["id", "title", "image", "value", "type", "used", "priceTitle"]

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
        """Create an instance of TenantQuotaFeatureDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of used
        if self.used:
            _dict['used'] = self.used.to_dict()
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if image (nullable) is None
        # and model_fields_set contains the field
        if self.image is None and "image" in self.model_fields_set:
            _dict['image'] = None

        # set to None if value (nullable) is None
        # and model_fields_set contains the field
        if self.value is None and "value" in self.model_fields_set:
            _dict['value'] = None

        # set to None if type (nullable) is None
        # and model_fields_set contains the field
        if self.type is None and "type" in self.model_fields_set:
            _dict['type'] = None

        # set to None if price_title (nullable) is None
        # and model_fields_set contains the field
        if self.price_title is None and "price_title" in self.model_fields_set:
            _dict['priceTitle'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of TenantQuotaFeatureDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "title": obj.get("title"),
            "image": obj.get("image"),
            "value": obj.get("value"),
            "type": obj.get("type"),
            "used": FeatureUsedDto.from_dict(obj["used"]) if obj.get("used") is not None else None,
            "priceTitle": obj.get("priceTitle")
        })
        return _obj


