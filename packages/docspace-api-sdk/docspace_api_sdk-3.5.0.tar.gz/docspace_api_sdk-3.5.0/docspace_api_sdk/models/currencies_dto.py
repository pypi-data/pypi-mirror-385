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
from typing import Optional, Set
from typing_extensions import Self

class CurrenciesDto(BaseModel):
    """
    The currencies parameters.
    """ # noqa: E501
    iso_country_code: Optional[StrictStr] = Field(default=None, description="The ISO country code.", alias="isoCountryCode")
    iso_currency_symbol: Optional[StrictStr] = Field(default=None, description="The ISO currency symbol.", alias="isoCurrencySymbol")
    currency_native_name: Optional[StrictStr] = Field(default=None, description="The currency native name.", alias="currencyNativeName")
    __properties: ClassVar[List[str]] = ["isoCountryCode", "isoCurrencySymbol", "currencyNativeName"]

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
        """Create an instance of CurrenciesDto from a JSON string"""
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
        # set to None if iso_country_code (nullable) is None
        # and model_fields_set contains the field
        if self.iso_country_code is None and "iso_country_code" in self.model_fields_set:
            _dict['isoCountryCode'] = None

        # set to None if iso_currency_symbol (nullable) is None
        # and model_fields_set contains the field
        if self.iso_currency_symbol is None and "iso_currency_symbol" in self.model_fields_set:
            _dict['isoCurrencySymbol'] = None

        # set to None if currency_native_name (nullable) is None
        # and model_fields_set contains the field
        if self.currency_native_name is None and "currency_native_name" in self.model_fields_set:
            _dict['currencyNativeName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CurrenciesDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "isoCountryCode": obj.get("isoCountryCode"),
            "isoCurrencySymbol": obj.get("isoCurrencySymbol"),
            "currencyNativeName": obj.get("currencyNativeName")
        })
        return _obj


