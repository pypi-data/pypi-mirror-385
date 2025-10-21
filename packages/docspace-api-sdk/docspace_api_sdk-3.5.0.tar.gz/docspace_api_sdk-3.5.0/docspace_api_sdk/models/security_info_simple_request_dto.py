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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.file_share_params import FileShareParams
from typing import Optional, Set
from typing_extensions import Self

class SecurityInfoSimpleRequestDto(BaseModel):
    """
    The parameters of the security information request.
    """ # noqa: E501
    share: Optional[List[FileShareParams]] = Field(default=None, description="The collection of sharing parameters.")
    notify: Optional[StrictBool] = Field(default=None, description="Specifies whether to notify users about the shared file or not.")
    sharing_message: Optional[StrictStr] = Field(default=None, description="The message to send when notifying about the shared file.", alias="sharingMessage")
    __properties: ClassVar[List[str]] = ["share", "notify", "sharingMessage"]

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
        """Create an instance of SecurityInfoSimpleRequestDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in share (list)
        _items = []
        if self.share:
            for _item_share in self.share:
                if _item_share:
                    _items.append(_item_share.to_dict())
            _dict['share'] = _items
        # set to None if share (nullable) is None
        # and model_fields_set contains the field
        if self.share is None and "share" in self.model_fields_set:
            _dict['share'] = None

        # set to None if sharing_message (nullable) is None
        # and model_fields_set contains the field
        if self.sharing_message is None and "sharing_message" in self.model_fields_set:
            _dict['sharingMessage'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SecurityInfoSimpleRequestDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "share": [FileShareParams.from_dict(_item) for _item in obj["share"]] if obj.get("share") is not None else None,
            "notify": obj.get("notify"),
            "sharingMessage": obj.get("sharingMessage")
        })
        return _obj


