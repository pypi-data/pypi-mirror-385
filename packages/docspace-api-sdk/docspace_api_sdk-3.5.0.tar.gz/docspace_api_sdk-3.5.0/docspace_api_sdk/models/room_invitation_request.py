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
from docspace_api_sdk.models.room_invitation import RoomInvitation
from typing import Optional, Set
from typing_extensions import Self

class RoomInvitationRequest(BaseModel):
    """
    The request parameters for inviting users to the room.
    """ # noqa: E501
    invitations: Optional[List[RoomInvitation]] = Field(default=None, description="The collection of invitation parameters.")
    notify: Optional[StrictBool] = Field(default=None, description="Specifies whether to notify users about the shared room or not.")
    message: Optional[StrictStr] = Field(default=None, description="The message to send when notifying about the shared room.")
    culture: Optional[StrictStr] = Field(default=None, description="The language of the room invitation.")
    force: Optional[StrictBool] = Field(default=None, description="Specifies whether to forcibly delete a user with form roles from the room.")
    __properties: ClassVar[List[str]] = ["invitations", "notify", "message", "culture", "force"]

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
        """Create an instance of RoomInvitationRequest from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in invitations (list)
        _items = []
        if self.invitations:
            for _item_invitations in self.invitations:
                if _item_invitations:
                    _items.append(_item_invitations.to_dict())
            _dict['invitations'] = _items
        # set to None if invitations (nullable) is None
        # and model_fields_set contains the field
        if self.invitations is None and "invitations" in self.model_fields_set:
            _dict['invitations'] = None

        # set to None if message (nullable) is None
        # and model_fields_set contains the field
        if self.message is None and "message" in self.model_fields_set:
            _dict['message'] = None

        # set to None if culture (nullable) is None
        # and model_fields_set contains the field
        if self.culture is None and "culture" in self.model_fields_set:
            _dict['culture'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of RoomInvitationRequest from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "invitations": [RoomInvitation.from_dict(_item) for _item in obj["invitations"]] if obj.get("invitations") is not None else None,
            "notify": obj.get("notify"),
            "message": obj.get("message"),
            "culture": obj.get("culture"),
            "force": obj.get("force")
        })
        return _obj


