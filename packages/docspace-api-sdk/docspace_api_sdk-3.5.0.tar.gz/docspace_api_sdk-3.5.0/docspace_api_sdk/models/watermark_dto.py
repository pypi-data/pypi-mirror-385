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
from docspace_api_sdk.models.watermark_additions import WatermarkAdditions
from typing import Optional, Set
from typing_extensions import Self

class WatermarkDto(BaseModel):
    """
    The watermark settings.
    """ # noqa: E501
    additions: WatermarkAdditions
    text: Optional[StrictStr] = Field(default=None, description="The watermark text.")
    rotate: StrictInt = Field(description="The watermark text and image rotate.")
    image_scale: StrictInt = Field(description="The watermark image scale.", alias="imageScale")
    image_url: Optional[StrictStr] = Field(default=None, description="The watermark image url.", alias="imageUrl")
    image_height: Union[StrictFloat, StrictInt] = Field(description="The watermark image height.", alias="imageHeight")
    image_width: Union[StrictFloat, StrictInt] = Field(description="The watermark image width.", alias="imageWidth")
    __properties: ClassVar[List[str]] = ["additions", "text", "rotate", "imageScale", "imageUrl", "imageHeight", "imageWidth"]

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
        """Create an instance of WatermarkDto from a JSON string"""
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
        # set to None if text (nullable) is None
        # and model_fields_set contains the field
        if self.text is None and "text" in self.model_fields_set:
            _dict['text'] = None

        # set to None if image_url (nullable) is None
        # and model_fields_set contains the field
        if self.image_url is None and "image_url" in self.model_fields_set:
            _dict['imageUrl'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WatermarkDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "additions": obj.get("additions"),
            "text": obj.get("text"),
            "rotate": obj.get("rotate"),
            "imageScale": obj.get("imageScale"),
            "imageUrl": obj.get("imageUrl"),
            "imageHeight": obj.get("imageHeight"),
            "imageWidth": obj.get("imageWidth")
        })
        return _obj


