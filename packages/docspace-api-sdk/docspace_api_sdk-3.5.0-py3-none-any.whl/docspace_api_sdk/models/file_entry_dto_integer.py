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
from inspect import getfullargspec
import json
import pprint
import re  # noqa: F401
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.employee_dto import EmployeeDto
from docspace_api_sdk.models.file_entry_dto_integer_all_of_available_share_rights import FileEntryDtoIntegerAllOfAvailableShareRights
from docspace_api_sdk.models.file_entry_dto_integer_all_of_security import FileEntryDtoIntegerAllOfSecurity
from docspace_api_sdk.models.file_entry_dto_integer_all_of_share_settings import FileEntryDtoIntegerAllOfShareSettings
from docspace_api_sdk.models.file_entry_type import FileEntryType
from docspace_api_sdk.models.file_share import FileShare
from docspace_api_sdk.models.folder_type import FolderType
from typing import Union, Any, List, Set, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal, Self
from pydantic import Field
from docspace_api_sdk.models.file_entry_base_dto import FileEntryBaseDto

class FileEntryDtoInteger(FileEntryBaseDto):
    """
    The generic file entry information.
    """

    id: Optional[StrictInt] = Field(default=None, description="The file entry ID.")
    root_folder_id: Optional[StrictInt] = Field(default=None, description="The root folder ID of the file entry.", alias="rootFolderId")
    origin_id: Optional[StrictInt] = Field(default=None, description="The origin ID of the file entry.", alias="originId")
    origin_room_id: Optional[StrictInt] = Field(default=None, description="The origin room ID of the file entry.", alias="originRoomId")
    origin_title: Optional[StrictStr] = Field(default=None, description="The origin title of the file entry.", alias="originTitle")
    origin_room_title: Optional[StrictStr] = Field(default=None, description="The origin room title of the file entry.", alias="originRoomTitle")
    can_share: Optional[StrictBool] = Field(default=None, description="Specifies if the file entry can be shared or not.", alias="canShare")
    share_settings: Optional[FileEntryDtoIntegerAllOfShareSettings] = Field(default=None, alias="shareSettings")
    security: Optional[FileEntryDtoIntegerAllOfSecurity] = None
    available_share_rights: Optional[FileEntryDtoIntegerAllOfAvailableShareRights] = Field(default=None, alias="availableShareRights")
    request_token: Optional[StrictStr] = Field(default=None, description="The request token of the file entry.", alias="requestToken")
    external: Optional[StrictBool] = Field(default=None, description="Specifies if the folder can be accessed via an external link or not.")
    expiration_date: Optional[ApiDateTime] = Field(default=None, alias="expirationDate")
    is_link_expired: Optional[StrictBool] = Field(default=None, description="Indicates whether the shareable link associated with the file or folder has expired.", alias="isLinkExpired")

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
        """Create an instance of FileEntryDtoInteger from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of created
        if self.created:
            _dict['created'] = self.created.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created_by
        if self.created_by:
            _dict['createdBy'] = self.created_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of updated
        if self.updated:
            _dict['updated'] = self.updated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of auto_delete
        if self.auto_delete:
            _dict['autoDelete'] = self.auto_delete.to_dict()
        # override the default output from pydantic by calling `to_dict()` of updated_by
        if self.updated_by:
            _dict['updatedBy'] = self.updated_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of share_settings
        if self.share_settings:
            _dict['shareSettings'] = self.share_settings.to_dict()
        # override the default output from pydantic by calling `to_dict()` of security
        if self.security:
            _dict['security'] = self.security.to_dict()
        # override the default output from pydantic by calling `to_dict()` of available_share_rights
        if self.available_share_rights:
            _dict['availableShareRights'] = self.available_share_rights.to_dict()
        # override the default output from pydantic by calling `to_dict()` of expiration_date
        if self.expiration_date:
            _dict['expirationDate'] = self.expiration_date.to_dict()
        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if short_web_url (nullable) is None
        # and model_fields_set contains the field
        if self.short_web_url is None and "short_web_url" in self.model_fields_set:
            _dict['shortWebUrl'] = None

        # set to None if provider_item (nullable) is None
        # and model_fields_set contains the field
        if self.provider_item is None and "provider_item" in self.model_fields_set:
            _dict['providerItem'] = None

        # set to None if provider_key (nullable) is None
        # and model_fields_set contains the field
        if self.provider_key is None and "provider_key" in self.model_fields_set:
            _dict['providerKey'] = None

        # set to None if provider_id (nullable) is None
        # and model_fields_set contains the field
        if self.provider_id is None and "provider_id" in self.model_fields_set:
            _dict['providerId'] = None

        # set to None if order (nullable) is None
        # and model_fields_set contains the field
        if self.order is None and "order" in self.model_fields_set:
            _dict['order'] = None

        # set to None if is_favorite (nullable) is None
        # and model_fields_set contains the field
        if self.is_favorite is None and "is_favorite" in self.model_fields_set:
            _dict['isFavorite'] = None

        # set to None if origin_title (nullable) is None
        # and model_fields_set contains the field
        if self.origin_title is None and "origin_title" in self.model_fields_set:
            _dict['originTitle'] = None

        # set to None if origin_room_title (nullable) is None
        # and model_fields_set contains the field
        if self.origin_room_title is None and "origin_room_title" in self.model_fields_set:
            _dict['originRoomTitle'] = None

        # set to None if share_settings (nullable) is None
        # and model_fields_set contains the field
        if self.share_settings is None and "share_settings" in self.model_fields_set:
            _dict['shareSettings'] = None

        # set to None if security (nullable) is None
        # and model_fields_set contains the field
        if self.security is None and "security" in self.model_fields_set:
            _dict['security'] = None

        # set to None if available_share_rights (nullable) is None
        # and model_fields_set contains the field
        if self.available_share_rights is None and "available_share_rights" in self.model_fields_set:
            _dict['availableShareRights'] = None

        # set to None if request_token (nullable) is None
        # and model_fields_set contains the field
        if self.request_token is None and "request_token" in self.model_fields_set:
            _dict['requestToken'] = None

        # set to None if external (nullable) is None
        # and model_fields_set contains the field
        if self.external is None and "external" in self.model_fields_set:
            _dict['external'] = None

        # set to None if is_link_expired (nullable) is None
        # and model_fields_set contains the field
        if self.is_link_expired is None and "is_link_expired" in self.model_fields_set:
            _dict['isLinkExpired'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance from a dict"""
        if obj is None:
            return None
        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        base_obj = super().from_dict(obj)

        extra_fields = cls.model_validate({
            "id": obj.get("id"),
            "rootFolderId": obj.get("rootFolderId"),
            "originId": obj.get("originId"),
            "originRoomId": obj.get("originRoomId"),
            "originTitle": obj.get("originTitle"),
            "originRoomTitle": obj.get("originRoomTitle"),
            "canShare": obj.get("canShare"),
            "shareSettings": FileEntryDtoIntegerAllOfShareSettings.from_dict(obj["shareSettings"]) if obj.get("shareSettings") is not None else None,
            "security": FileEntryDtoIntegerAllOfSecurity.from_dict(obj["security"]) if obj.get("security") is not None else None,
            "availableShareRights": FileEntryDtoIntegerAllOfAvailableShareRights.from_dict(obj["availableShareRights"]) if obj.get("availableShareRights") is not None else None,
            "requestToken": obj.get("requestToken"),
            "external": obj.get("external"),
            "expirationDate": ApiDateTime.from_dict(obj["expirationDate"]) if obj.get("expirationDate") is not None else None,
            "isLinkExpired": obj.get("isLinkExpired")
        })
        return cls(**base_obj.model_dump(), **extra_fields)

