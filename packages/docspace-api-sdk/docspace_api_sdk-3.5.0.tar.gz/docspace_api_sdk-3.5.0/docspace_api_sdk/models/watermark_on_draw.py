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
from docspace_api_sdk.models.paragraph import Paragraph
from typing import Optional, Set
from typing_extensions import Self

class WatermarkOnDraw(BaseModel):
    """
    The document watermark parameters.
    """ # noqa: E501
    width: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Defines the watermark width measured in millimeters.")
    height: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Defines the watermark height measured in millimeters.")
    margins: Optional[List[StrictInt]] = Field(default=None, description="Defines the watermark margins measured in millimeters.")
    fill: Optional[StrictStr] = Field(default=None, description="Defines the watermark fill color.")
    rotate: Optional[StrictInt] = Field(default=None, description="Defines the watermark rotation angle.")
    transparent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Defines the watermark transparency percentage.")
    paragraphs: Optional[List[Paragraph]] = Field(default=None, description="The list of paragraphs of the watermark.")
    __properties: ClassVar[List[str]] = ["width", "height", "margins", "fill", "rotate", "transparent", "paragraphs"]

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
        """Create an instance of WatermarkOnDraw from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in paragraphs (list)
        _items = []
        if self.paragraphs:
            for _item_paragraphs in self.paragraphs:
                if _item_paragraphs:
                    _items.append(_item_paragraphs.to_dict())
            _dict['paragraphs'] = _items
        # set to None if margins (nullable) is None
        # and model_fields_set contains the field
        if self.margins is None and "margins" in self.model_fields_set:
            _dict['margins'] = None

        # set to None if fill (nullable) is None
        # and model_fields_set contains the field
        if self.fill is None and "fill" in self.model_fields_set:
            _dict['fill'] = None

        # set to None if paragraphs (nullable) is None
        # and model_fields_set contains the field
        if self.paragraphs is None and "paragraphs" in self.model_fields_set:
            _dict['paragraphs'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WatermarkOnDraw from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "width": obj.get("width"),
            "height": obj.get("height"),
            "margins": obj.get("margins"),
            "fill": obj.get("fill"),
            "rotate": obj.get("rotate"),
            "transparent": obj.get("transparent"),
            "paragraphs": [Paragraph.from_dict(_item) for _item in obj["paragraphs"]] if obj.get("paragraphs") is not None else None
        })
        return _obj


