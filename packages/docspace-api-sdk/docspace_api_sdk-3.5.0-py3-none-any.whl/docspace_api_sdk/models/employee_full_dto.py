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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.contact import Contact
from docspace_api_sdk.models.dark_theme_settings_type import DarkThemeSettingsType
from docspace_api_sdk.models.employee_activation_status import EmployeeActivationStatus
from docspace_api_sdk.models.employee_dto import EmployeeDto
from docspace_api_sdk.models.employee_status import EmployeeStatus
from docspace_api_sdk.models.group_summary_dto import GroupSummaryDto
from docspace_api_sdk.models.mobile_phone_activation_status import MobilePhoneActivationStatus
from typing import Union, Any, List, Set, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal, Self
from pydantic import Field
from docspace_api_sdk.models.employee_dto import EmployeeDto

class EmployeeFullDto(EmployeeDto):
    """
    The full list of user parameters.
    """

    first_name: Optional[StrictStr] = Field(default=None, description="The user first name.", alias="firstName")
    last_name: Optional[StrictStr] = Field(default=None, description="The user last name.", alias="lastName")
    user_name: Optional[StrictStr] = Field(default=None, description="The user username.", alias="userName")
    email: Optional[StrictStr] = Field(default=None, description="The user email.")
    contacts: Optional[List[Contact]] = Field(default=None, description="The list of user contacts.")
    birthday: Optional[ApiDateTime] = None
    sex: Optional[StrictStr] = Field(default=None, description="The user sex.")
    status: Optional[EmployeeStatus] = None
    activation_status: Optional[EmployeeActivationStatus] = Field(default=None, alias="activationStatus")
    terminated: Optional[ApiDateTime] = None
    department: Optional[StrictStr] = Field(default=None, description="The user department.")
    work_from: Optional[ApiDateTime] = Field(default=None, alias="workFrom")
    groups: Optional[List[GroupSummaryDto]] = Field(default=None, description="The list of user groups.")
    location: Optional[StrictStr] = Field(default=None, description="The user location.")
    notes: Optional[StrictStr] = Field(default=None, description="The user notes.")
    is_admin: Optional[StrictBool] = Field(default=None, description="Specifies if the user is an administrator or not.", alias="isAdmin")
    is_room_admin: Optional[StrictBool] = Field(default=None, description="Specifies if the user is a room administrator or not.", alias="isRoomAdmin")
    is_ldap: Optional[StrictBool] = Field(default=None, description="Specifies if the LDAP settings are enabled for the user or not.", alias="isLDAP")
    list_admin_modules: Optional[List[StrictStr]] = Field(default=None, description="The list of the administrator modules.", alias="listAdminModules")
    is_owner: Optional[StrictBool] = Field(default=None, description="Specifies if the user is a portal owner or not.", alias="isOwner")
    is_visitor: Optional[StrictBool] = Field(default=None, description="Specifies if the user is a portal visitor or not.", alias="isVisitor")
    is_collaborator: Optional[StrictBool] = Field(default=None, description="Specifies if the user is a portal collaborator or not.", alias="isCollaborator")
    culture_name: Optional[StrictStr] = Field(default=None, description="The user culture code.", alias="cultureName")
    mobile_phone: Optional[StrictStr] = Field(default=None, description="The user mobile phone number.", alias="mobilePhone")
    mobile_phone_activation_status: Optional[MobilePhoneActivationStatus] = Field(default=None, alias="mobilePhoneActivationStatus")
    is_sso: Optional[StrictBool] = Field(default=None, description="Specifies if the SSO settings are enabled for the user or not.", alias="isSSO")
    theme: Optional[DarkThemeSettingsType] = None
    quota_limit: Optional[StrictInt] = Field(default=None, description="The user quota limit.", alias="quotaLimit")
    used_space: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The portal used space of the user.", alias="usedSpace")
    shared: Optional[StrictBool] = Field(default=None, description="Specifies if the user has access rights.")
    is_custom_quota: Optional[StrictBool] = Field(default=None, description="Specifies if the user has a custom quota or not.", alias="isCustomQuota")
    login_event_id: Optional[StrictInt] = Field(default=None, description="The current login event ID.", alias="loginEventId")
    created_by: Optional[EmployeeDto] = Field(default=None, alias="createdBy")
    registration_date: Optional[ApiDateTime] = Field(default=None, alias="registrationDate")
    has_personal_folder: Optional[StrictBool] = Field(default=None, description="Specifies if the user has a personal folder or not.", alias="hasPersonalFolder")
    tfa_app_enabled: Optional[StrictBool] = Field(default=None, description="Indicates whether the user has enabled two-factor authentication (TFA) using an authentication app.", alias="tfaAppEnabled")

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
        """Create an instance of EmployeeFullDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in contacts (list)
        _items = []
        if self.contacts:
            for _item_contacts in self.contacts:
                if _item_contacts:
                    _items.append(_item_contacts.to_dict())
            _dict['contacts'] = _items
        # override the default output from pydantic by calling `to_dict()` of birthday
        if self.birthday:
            _dict['birthday'] = self.birthday.to_dict()
        # override the default output from pydantic by calling `to_dict()` of terminated
        if self.terminated:
            _dict['terminated'] = self.terminated.to_dict()
        # override the default output from pydantic by calling `to_dict()` of work_from
        if self.work_from:
            _dict['workFrom'] = self.work_from.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in groups (list)
        _items = []
        if self.groups:
            for _item_groups in self.groups:
                if _item_groups:
                    _items.append(_item_groups.to_dict())
            _dict['groups'] = _items
        # override the default output from pydantic by calling `to_dict()` of created_by
        if self.created_by:
            _dict['createdBy'] = self.created_by.to_dict()
        # override the default output from pydantic by calling `to_dict()` of registration_date
        if self.registration_date:
            _dict['registrationDate'] = self.registration_date.to_dict()
        # set to None if display_name (nullable) is None
        # and model_fields_set contains the field
        if self.display_name is None and "display_name" in self.model_fields_set:
            _dict['displayName'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if avatar (nullable) is None
        # and model_fields_set contains the field
        if self.avatar is None and "avatar" in self.model_fields_set:
            _dict['avatar'] = None

        # set to None if avatar_original (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_original is None and "avatar_original" in self.model_fields_set:
            _dict['avatarOriginal'] = None

        # set to None if avatar_max (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_max is None and "avatar_max" in self.model_fields_set:
            _dict['avatarMax'] = None

        # set to None if avatar_medium (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_medium is None and "avatar_medium" in self.model_fields_set:
            _dict['avatarMedium'] = None

        # set to None if avatar_small (nullable) is None
        # and model_fields_set contains the field
        if self.avatar_small is None and "avatar_small" in self.model_fields_set:
            _dict['avatarSmall'] = None

        # set to None if profile_url (nullable) is None
        # and model_fields_set contains the field
        if self.profile_url is None and "profile_url" in self.model_fields_set:
            _dict['profileUrl'] = None

        # set to None if first_name (nullable) is None
        # and model_fields_set contains the field
        if self.first_name is None and "first_name" in self.model_fields_set:
            _dict['firstName'] = None

        # set to None if last_name (nullable) is None
        # and model_fields_set contains the field
        if self.last_name is None and "last_name" in self.model_fields_set:
            _dict['lastName'] = None

        # set to None if user_name (nullable) is None
        # and model_fields_set contains the field
        if self.user_name is None and "user_name" in self.model_fields_set:
            _dict['userName'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if contacts (nullable) is None
        # and model_fields_set contains the field
        if self.contacts is None and "contacts" in self.model_fields_set:
            _dict['contacts'] = None

        # set to None if sex (nullable) is None
        # and model_fields_set contains the field
        if self.sex is None and "sex" in self.model_fields_set:
            _dict['sex'] = None

        # set to None if department (nullable) is None
        # and model_fields_set contains the field
        if self.department is None and "department" in self.model_fields_set:
            _dict['department'] = None

        # set to None if groups (nullable) is None
        # and model_fields_set contains the field
        if self.groups is None and "groups" in self.model_fields_set:
            _dict['groups'] = None

        # set to None if location (nullable) is None
        # and model_fields_set contains the field
        if self.location is None and "location" in self.model_fields_set:
            _dict['location'] = None

        # set to None if notes (nullable) is None
        # and model_fields_set contains the field
        if self.notes is None and "notes" in self.model_fields_set:
            _dict['notes'] = None

        # set to None if list_admin_modules (nullable) is None
        # and model_fields_set contains the field
        if self.list_admin_modules is None and "list_admin_modules" in self.model_fields_set:
            _dict['listAdminModules'] = None

        # set to None if culture_name (nullable) is None
        # and model_fields_set contains the field
        if self.culture_name is None and "culture_name" in self.model_fields_set:
            _dict['cultureName'] = None

        # set to None if mobile_phone (nullable) is None
        # and model_fields_set contains the field
        if self.mobile_phone is None and "mobile_phone" in self.model_fields_set:
            _dict['mobilePhone'] = None

        # set to None if quota_limit (nullable) is None
        # and model_fields_set contains the field
        if self.quota_limit is None and "quota_limit" in self.model_fields_set:
            _dict['quotaLimit'] = None

        # set to None if used_space (nullable) is None
        # and model_fields_set contains the field
        if self.used_space is None and "used_space" in self.model_fields_set:
            _dict['usedSpace'] = None

        # set to None if shared (nullable) is None
        # and model_fields_set contains the field
        if self.shared is None and "shared" in self.model_fields_set:
            _dict['shared'] = None

        # set to None if is_custom_quota (nullable) is None
        # and model_fields_set contains the field
        if self.is_custom_quota is None and "is_custom_quota" in self.model_fields_set:
            _dict['isCustomQuota'] = None

        # set to None if login_event_id (nullable) is None
        # and model_fields_set contains the field
        if self.login_event_id is None and "login_event_id" in self.model_fields_set:
            _dict['loginEventId'] = None

        # set to None if tfa_app_enabled (nullable) is None
        # and model_fields_set contains the field
        if self.tfa_app_enabled is None and "tfa_app_enabled" in self.model_fields_set:
            _dict['tfaAppEnabled'] = None

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
            "firstName": obj.get("firstName"),
            "lastName": obj.get("lastName"),
            "userName": obj.get("userName"),
            "email": obj.get("email"),
            "contacts": [Contact.from_dict(_item) for _item in obj["contacts"]] if obj.get("contacts") is not None else None,
            "birthday": ApiDateTime.from_dict(obj["birthday"]) if obj.get("birthday") is not None else None,
            "sex": obj.get("sex"),
            "status": obj.get("status"),
            "activationStatus": obj.get("activationStatus"),
            "terminated": ApiDateTime.from_dict(obj["terminated"]) if obj.get("terminated") is not None else None,
            "department": obj.get("department"),
            "workFrom": ApiDateTime.from_dict(obj["workFrom"]) if obj.get("workFrom") is not None else None,
            "groups": [GroupSummaryDto.from_dict(_item) for _item in obj["groups"]] if obj.get("groups") is not None else None,
            "location": obj.get("location"),
            "notes": obj.get("notes"),
            "isAdmin": obj.get("isAdmin"),
            "isRoomAdmin": obj.get("isRoomAdmin"),
            "isLDAP": obj.get("isLDAP"),
            "listAdminModules": obj.get("listAdminModules"),
            "isOwner": obj.get("isOwner"),
            "isVisitor": obj.get("isVisitor"),
            "isCollaborator": obj.get("isCollaborator"),
            "cultureName": obj.get("cultureName"),
            "mobilePhone": obj.get("mobilePhone"),
            "mobilePhoneActivationStatus": obj.get("mobilePhoneActivationStatus"),
            "isSSO": obj.get("isSSO"),
            "theme": obj.get("theme"),
            "quotaLimit": obj.get("quotaLimit"),
            "usedSpace": obj.get("usedSpace"),
            "shared": obj.get("shared"),
            "isCustomQuota": obj.get("isCustomQuota"),
            "loginEventId": obj.get("loginEventId"),
            "createdBy": EmployeeDto.from_dict(obj["createdBy"]) if obj.get("createdBy") is not None else None,
            "registrationDate": ApiDateTime.from_dict(obj["registrationDate"]) if obj.get("registrationDate") is not None else None,
            "hasPersonalFolder": obj.get("hasPersonalFolder"),
            "tfaAppEnabled": obj.get("tfaAppEnabled")
        })
        return cls(**base_obj.model_dump(), **extra_fields)

