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
from docspace_api_sdk.models.logo import Logo
from docspace_api_sdk.models.room_data_lifetime_dto import RoomDataLifetimeDto
from docspace_api_sdk.models.room_type import RoomType
from docspace_api_sdk.models.watermark_dto import WatermarkDto
from typing import Union, Any, List, Set, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal, Self
from pydantic import Field
from docspace_api_sdk.models.file_entry_dto_string import FileEntryDtoString

class FolderDtoString(FileEntryDtoString):
    """
    The folder parameters.
    """

    parent_id: Optional[StrictStr] = Field(default=None, description="The parent folder ID of the folder.", alias="parentId")
    files_count: Optional[StrictInt] = Field(default=None, description="The number of files that the folder contains.", alias="filesCount")
    folders_count: Optional[StrictInt] = Field(default=None, description="The number of folders that the folder contains.", alias="foldersCount")
    is_shareable: Optional[StrictBool] = Field(default=None, description="Specifies if the folder can be shared or not.", alias="isShareable")
    new: Optional[StrictInt] = Field(default=None, description="The new element index in the folder.")
    mute: Optional[StrictBool] = Field(default=None, description="Specifies if the folder notifications are enabled or not.")
    tags: Optional[List[StrictStr]] = Field(default=None, description="The list of tags of the folder.")
    logo: Optional[Logo] = None
    pinned: Optional[StrictBool] = Field(default=None, description="Specifies if the folder is pinned or not.")
    room_type: Optional[RoomType] = Field(default=None, alias="roomType")
    private: Optional[StrictBool] = Field(default=None, description="Specifies if the folder is private or not.")
    indexing: Optional[StrictBool] = Field(default=None, description="Specifies if the folder is indexed or not.")
    deny_download: Optional[StrictBool] = Field(default=None, description="Specifies if the folder can be downloaded or not.", alias="denyDownload")
    lifetime: Optional[RoomDataLifetimeDto] = None
    watermark: Optional[WatermarkDto] = None
    type: Optional[FolderType] = None
    in_room: Optional[StrictBool] = Field(default=None, description="Specifies if the folder is placed in the room or not.", alias="inRoom")
    quota_limit: Optional[StrictInt] = Field(default=None, description="The folder quota limit.", alias="quotaLimit")
    is_custom_quota: Optional[StrictBool] = Field(default=None, description="Specifies if the folder room has a custom quota or not.", alias="isCustomQuota")
    used_space: Optional[StrictInt] = Field(default=None, description="How much folder space is used (counter).", alias="usedSpace")
    password_protected: Optional[StrictBool] = Field(default=None, description="Specifies if the folder is password protected or not.", alias="passwordProtected")
    expired: Optional[StrictBool] = Field(default=None, description="Specifies if an external link to the folder is expired or not.")

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
        """Create an instance of FolderDtoString from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of logo
        if self.logo:
            _dict['logo'] = self.logo.to_dict()
        # override the default output from pydantic by calling `to_dict()` of lifetime
        if self.lifetime:
            _dict['lifetime'] = self.lifetime.to_dict()
        # override the default output from pydantic by calling `to_dict()` of watermark
        if self.watermark:
            _dict['watermark'] = self.watermark.to_dict()
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

        # set to None if id (nullable) is None
        # and model_fields_set contains the field
        if self.id is None and "id" in self.model_fields_set:
            _dict['id'] = None

        # set to None if root_folder_id (nullable) is None
        # and model_fields_set contains the field
        if self.root_folder_id is None and "root_folder_id" in self.model_fields_set:
            _dict['rootFolderId'] = None

        # set to None if origin_id (nullable) is None
        # and model_fields_set contains the field
        if self.origin_id is None and "origin_id" in self.model_fields_set:
            _dict['originId'] = None

        # set to None if origin_room_id (nullable) is None
        # and model_fields_set contains the field
        if self.origin_room_id is None and "origin_room_id" in self.model_fields_set:
            _dict['originRoomId'] = None

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

        # set to None if parent_id (nullable) is None
        # and model_fields_set contains the field
        if self.parent_id is None and "parent_id" in self.model_fields_set:
            _dict['parentId'] = None

        # set to None if is_shareable (nullable) is None
        # and model_fields_set contains the field
        if self.is_shareable is None and "is_shareable" in self.model_fields_set:
            _dict['isShareable'] = None

        # set to None if tags (nullable) is None
        # and model_fields_set contains the field
        if self.tags is None and "tags" in self.model_fields_set:
            _dict['tags'] = None

        # set to None if in_room (nullable) is None
        # and model_fields_set contains the field
        if self.in_room is None and "in_room" in self.model_fields_set:
            _dict['inRoom'] = None

        # set to None if quota_limit (nullable) is None
        # and model_fields_set contains the field
        if self.quota_limit is None and "quota_limit" in self.model_fields_set:
            _dict['quotaLimit'] = None

        # set to None if is_custom_quota (nullable) is None
        # and model_fields_set contains the field
        if self.is_custom_quota is None and "is_custom_quota" in self.model_fields_set:
            _dict['isCustomQuota'] = None

        # set to None if used_space (nullable) is None
        # and model_fields_set contains the field
        if self.used_space is None and "used_space" in self.model_fields_set:
            _dict['usedSpace'] = None

        # set to None if password_protected (nullable) is None
        # and model_fields_set contains the field
        if self.password_protected is None and "password_protected" in self.model_fields_set:
            _dict['passwordProtected'] = None

        # set to None if expired (nullable) is None
        # and model_fields_set contains the field
        if self.expired is None and "expired" in self.model_fields_set:
            _dict['expired'] = None

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
            "parentId": obj.get("parentId"),
            "filesCount": obj.get("filesCount"),
            "foldersCount": obj.get("foldersCount"),
            "isShareable": obj.get("isShareable"),
            "new": obj.get("new"),
            "mute": obj.get("mute"),
            "tags": obj.get("tags"),
            "logo": Logo.from_dict(obj["logo"]) if obj.get("logo") is not None else None,
            "pinned": obj.get("pinned"),
            "roomType": obj.get("roomType"),
            "private": obj.get("private"),
            "indexing": obj.get("indexing"),
            "denyDownload": obj.get("denyDownload"),
            "lifetime": RoomDataLifetimeDto.from_dict(obj["lifetime"]) if obj.get("lifetime") is not None else None,
            "watermark": WatermarkDto.from_dict(obj["watermark"]) if obj.get("watermark") is not None else None,
            "type": obj.get("type"),
            "inRoom": obj.get("inRoom"),
            "quotaLimit": obj.get("quotaLimit"),
            "isCustomQuota": obj.get("isCustomQuota"),
            "usedSpace": obj.get("usedSpace"),
            "passwordProtected": obj.get("passwordProtected"),
            "expired": obj.get("expired")
        })
        return cls(**base_obj.model_dump(), **extra_fields)

