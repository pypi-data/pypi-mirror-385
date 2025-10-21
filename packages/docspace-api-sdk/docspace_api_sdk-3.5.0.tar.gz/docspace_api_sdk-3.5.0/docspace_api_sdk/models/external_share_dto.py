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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.file_entry_type import FileEntryType
from docspace_api_sdk.models.status import Status
from typing import Optional, Set
from typing_extensions import Self

class ExternalShareDto(BaseModel):
    """
    The external sharing information and validation data.
    """ # noqa: E501
    status: Status
    id: Optional[StrictStr] = Field(description="The external data ID.")
    title: Optional[StrictStr] = Field(description="The external data title.")
    type: Optional[FileEntryType] = None
    tenant_id: StrictInt = Field(description="The tenant ID.", alias="tenantId")
    entity_id: Optional[StrictStr] = Field(default=None, description="The unique identifier of the shared entity.", alias="entityId")
    entity_title: Optional[StrictStr] = Field(default=None, description="The title of the shared entity.", alias="entityTitle")
    entity_type: Optional[FileEntryType] = Field(default=None, alias="entityType")
    is_room: Optional[StrictBool] = Field(default=None, description="Indicates whether the entity represents a room.", alias="isRoom")
    shared: StrictBool = Field(description="Specifies whether to share the external data or not.")
    link_id: StrictStr = Field(description="The link ID of the external data.", alias="linkId")
    is_authenticated: StrictBool = Field(description="Specifies whether the user is authenticated or not.", alias="isAuthenticated")
    is_room_member: Optional[StrictBool] = Field(default=None, description="The room ID of the external data.", alias="isRoomMember")
    __properties: ClassVar[List[str]] = ["status", "id", "title", "type", "tenantId", "entityId", "entityTitle", "entityType", "isRoom", "shared", "linkId", "isAuthenticated", "isRoomMember"]

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
        """Create an instance of ExternalShareDto from a JSON string"""
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
        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if entity_id (nullable) is None
        # and model_fields_set contains the field
        if self.entity_id is None and "entity_id" in self.model_fields_set:
            _dict['entityId'] = None

        # set to None if entity_title (nullable) is None
        # and model_fields_set contains the field
        if self.entity_title is None and "entity_title" in self.model_fields_set:
            _dict['entityTitle'] = None

        # set to None if is_room (nullable) is None
        # and model_fields_set contains the field
        if self.is_room is None and "is_room" in self.model_fields_set:
            _dict['isRoom'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ExternalShareDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "status": obj.get("status"),
            "id": obj.get("id"),
            "title": obj.get("title"),
            "type": obj.get("type"),
            "tenantId": obj.get("tenantId"),
            "entityId": obj.get("entityId"),
            "entityTitle": obj.get("entityTitle"),
            "entityType": obj.get("entityType"),
            "isRoom": obj.get("isRoom"),
            "shared": obj.get("shared"),
            "linkId": obj.get("linkId"),
            "isAuthenticated": obj.get("isAuthenticated"),
            "isRoomMember": obj.get("isRoomMember")
        })
        return _obj


