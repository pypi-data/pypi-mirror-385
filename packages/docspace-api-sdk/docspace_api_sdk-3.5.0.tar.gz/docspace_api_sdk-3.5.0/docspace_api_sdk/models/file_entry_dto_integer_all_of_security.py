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

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class FileEntryDtoIntegerAllOfSecurity(BaseModel):
    """
    The actions that can be performed with the file entry.
    """ # noqa: E501
    read: Optional[StrictBool] = Field(default=None, alias="Read")
    comment: Optional[StrictBool] = Field(default=None, alias="Comment")
    fill_forms: Optional[StrictBool] = Field(default=None, alias="FillForms")
    review: Optional[StrictBool] = Field(default=None, alias="Review")
    create: Optional[StrictBool] = Field(default=None, alias="Create")
    create_from: Optional[StrictBool] = Field(default=None, alias="CreateFrom")
    edit: Optional[StrictBool] = Field(default=None, alias="Edit")
    delete: Optional[StrictBool] = Field(default=None, alias="Delete")
    custom_filter: Optional[StrictBool] = Field(default=None, alias="CustomFilter")
    edit_room: Optional[StrictBool] = Field(default=None, alias="EditRoom")
    rename: Optional[StrictBool] = Field(default=None, alias="Rename")
    read_history: Optional[StrictBool] = Field(default=None, alias="ReadHistory")
    lock: Optional[StrictBool] = Field(default=None, alias="Lock")
    edit_history: Optional[StrictBool] = Field(default=None, alias="EditHistory")
    copy_to: Optional[StrictBool] = Field(default=None, alias="CopyTo")
    copy: Optional[StrictBool] = Field(default=None, alias="Copy")
    move_to: Optional[StrictBool] = Field(default=None, alias="MoveTo")
    move: Optional[StrictBool] = Field(default=None, alias="Move")
    pin: Optional[StrictBool] = Field(default=None, alias="Pin")
    mute: Optional[StrictBool] = Field(default=None, alias="Mute")
    edit_access: Optional[StrictBool] = Field(default=None, alias="EditAccess")
    duplicate: Optional[StrictBool] = Field(default=None, alias="Duplicate")
    submit_to_form_gallery: Optional[StrictBool] = Field(default=None, alias="SubmitToFormGallery")
    download: Optional[StrictBool] = Field(default=None, alias="Download")
    convert: Optional[StrictBool] = Field(default=None, alias="Convert")
    copy_shared_link: Optional[StrictBool] = Field(default=None, alias="CopySharedLink")
    read_links: Optional[StrictBool] = Field(default=None, alias="ReadLinks")
    reconnect: Optional[StrictBool] = Field(default=None, alias="Reconnect")
    create_room_from: Optional[StrictBool] = Field(default=None, alias="CreateRoomFrom")
    copy_link: Optional[StrictBool] = Field(default=None, alias="CopyLink")
    embed: Optional[StrictBool] = Field(default=None, alias="Embed")
    change_owner: Optional[StrictBool] = Field(default=None, alias="ChangeOwner")
    index_export: Optional[StrictBool] = Field(default=None, alias="IndexExport")
    start_filling: Optional[StrictBool] = Field(default=None, alias="StartFilling")
    filling_status: Optional[StrictBool] = Field(default=None, alias="FillingStatus")
    reset_filling: Optional[StrictBool] = Field(default=None, alias="ResetFilling")
    stop_filling: Optional[StrictBool] = Field(default=None, alias="StopFilling")
    open_form: Optional[StrictBool] = Field(default=None, alias="OpenForm")
    edit_internal: Optional[StrictBool] = Field(default=None, alias="EditInternal")
    edit_expiration: Optional[StrictBool] = Field(default=None, alias="EditExpiration")
    __properties: ClassVar[List[str]] = ["Read", "Comment", "FillForms", "Review", "Create", "CreateFrom", "Edit", "Delete", "CustomFilter", "EditRoom", "Rename", "ReadHistory", "Lock", "EditHistory", "CopyTo", "Copy", "MoveTo", "Move", "Pin", "Mute", "EditAccess", "Duplicate", "SubmitToFormGallery", "Download", "Convert", "CopySharedLink", "ReadLinks", "Reconnect", "CreateRoomFrom", "CopyLink", "Embed", "ChangeOwner", "IndexExport", "StartFilling", "FillingStatus", "ResetFilling", "StopFilling", "OpenForm", "EditInternal", "EditExpiration"]

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
        """Create an instance of FileEntryDtoIntegerAllOfSecurity from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FileEntryDtoIntegerAllOfSecurity from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "Read": obj.get("Read"),
            "Comment": obj.get("Comment"),
            "FillForms": obj.get("FillForms"),
            "Review": obj.get("Review"),
            "Create": obj.get("Create"),
            "CreateFrom": obj.get("CreateFrom"),
            "Edit": obj.get("Edit"),
            "Delete": obj.get("Delete"),
            "CustomFilter": obj.get("CustomFilter"),
            "EditRoom": obj.get("EditRoom"),
            "Rename": obj.get("Rename"),
            "ReadHistory": obj.get("ReadHistory"),
            "Lock": obj.get("Lock"),
            "EditHistory": obj.get("EditHistory"),
            "CopyTo": obj.get("CopyTo"),
            "Copy": obj.get("Copy"),
            "MoveTo": obj.get("MoveTo"),
            "Move": obj.get("Move"),
            "Pin": obj.get("Pin"),
            "Mute": obj.get("Mute"),
            "EditAccess": obj.get("EditAccess"),
            "Duplicate": obj.get("Duplicate"),
            "SubmitToFormGallery": obj.get("SubmitToFormGallery"),
            "Download": obj.get("Download"),
            "Convert": obj.get("Convert"),
            "CopySharedLink": obj.get("CopySharedLink"),
            "ReadLinks": obj.get("ReadLinks"),
            "Reconnect": obj.get("Reconnect"),
            "CreateRoomFrom": obj.get("CreateRoomFrom"),
            "CopyLink": obj.get("CopyLink"),
            "Embed": obj.get("Embed"),
            "ChangeOwner": obj.get("ChangeOwner"),
            "IndexExport": obj.get("IndexExport"),
            "StartFilling": obj.get("StartFilling"),
            "FillingStatus": obj.get("FillingStatus"),
            "ResetFilling": obj.get("ResetFilling"),
            "StopFilling": obj.get("StopFilling"),
            "OpenForm": obj.get("OpenForm"),
            "EditInternal": obj.get("EditInternal"),
            "EditExpiration": obj.get("EditExpiration")
        })
        return _obj


