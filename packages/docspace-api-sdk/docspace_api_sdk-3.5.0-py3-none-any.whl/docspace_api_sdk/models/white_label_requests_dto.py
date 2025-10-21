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
from typing_extensions import Annotated
from docspace_api_sdk.models.item_key_value_pair_string_logo_requests_dto import ItemKeyValuePairStringLogoRequestsDto
from typing import Optional, Set
from typing_extensions import Self

class WhiteLabelRequestsDto(BaseModel):
    """
    The request parameters for configuring the white label branding settings.
    """ # noqa: E501
    logo_text: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=40)]] = Field(default=None, description="The text to display alongside or in place of the logo.", alias="logoText")
    logo: Optional[List[ItemKeyValuePairStringLogoRequestsDto]] = Field(default=None, description="The white label tenant IDs with their logos (light or dark).")
    __properties: ClassVar[List[str]] = ["logoText", "logo"]

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
        """Create an instance of WhiteLabelRequestsDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in logo (list)
        _items = []
        if self.logo:
            for _item_logo in self.logo:
                if _item_logo:
                    _items.append(_item_logo.to_dict())
            _dict['logo'] = _items
        # set to None if logo_text (nullable) is None
        # and model_fields_set contains the field
        if self.logo_text is None and "logo_text" in self.model_fields_set:
            _dict['logoText'] = None

        # set to None if logo (nullable) is None
        # and model_fields_set contains the field
        if self.logo is None and "logo" in self.model_fields_set:
            _dict['logo'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WhiteLabelRequestsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "logoText": obj.get("logoText"),
            "logo": [ItemKeyValuePairStringLogoRequestsDto.from_dict(_item) for _item in obj["logo"]] if obj.get("logo") is not None else None
        })
        return _obj


