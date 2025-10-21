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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.employee_activation_status import EmployeeActivationStatus
from docspace_api_sdk.models.employee_status import EmployeeStatus
from docspace_api_sdk.models.mobile_phone_activation_status import MobilePhoneActivationStatus
from typing import Optional, Set
from typing_extensions import Self

class UserInfo(BaseModel):
    """
    The user information.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The user ID.")
    first_name: Optional[StrictStr] = Field(default=None, description="The user first name.", alias="firstName")
    last_name: Optional[StrictStr] = Field(default=None, description="The user last name.", alias="lastName")
    user_name: Optional[StrictStr] = Field(default=None, description="The user username.", alias="userName")
    birth_date: Optional[datetime] = Field(default=None, description="The user birthday.", alias="birthDate")
    sex: Optional[StrictBool] = Field(default=None, description="The user sex (male or female).")
    status: Optional[EmployeeStatus] = None
    activation_status: Optional[EmployeeActivationStatus] = Field(default=None, alias="activationStatus")
    terminated_date: Optional[datetime] = Field(default=None, description="The date and time when the user account was terminated.", alias="terminatedDate")
    title: Optional[StrictStr] = Field(default=None, description="The user title.")
    work_from_date: Optional[datetime] = Field(default=None, description="The user registration date.", alias="workFromDate")
    email: Optional[StrictStr] = Field(default=None, description="The user email address.")
    contacts: Optional[StrictStr] = Field(default=None, description="The list of user contacts in the string format.")
    contacts_list: Optional[List[StrictStr]] = Field(default=None, description="The list of user contacts.", alias="contactsList")
    location: Optional[StrictStr] = Field(default=None, description="The user location.")
    notes: Optional[StrictStr] = Field(default=None, description="The user notes.")
    removed: Optional[StrictBool] = Field(default=None, description="Specifies if the user account was removed or not.")
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the user account was last modified.", alias="lastModified")
    tenant_id: Optional[StrictInt] = Field(default=None, description="The tenant ID.", alias="tenantId")
    is_active: Optional[StrictBool] = Field(default=None, description="Specifies if the user is active or not.", alias="isActive")
    culture_name: Optional[StrictStr] = Field(default=None, description="The user culture code.", alias="cultureName")
    mobile_phone: Optional[StrictStr] = Field(default=None, description="The user mobile phone.", alias="mobilePhone")
    mobile_phone_activation_status: Optional[MobilePhoneActivationStatus] = Field(default=None, alias="mobilePhoneActivationStatus")
    sid: Optional[StrictStr] = Field(default=None, description="The LDAP user identificator.")
    ldap_qouta: Optional[StrictInt] = Field(default=None, description="The LDAP user quota attribute.", alias="ldapQouta")
    sso_name_id: Optional[StrictStr] = Field(default=None, description="The SSO SAML user identificator.", alias="ssoNameId")
    sso_session_id: Optional[StrictStr] = Field(default=None, description="The SSO SAML user session identificator.", alias="ssoSessionId")
    create_date: Optional[datetime] = Field(default=None, description="The date and time when the user account was created.", alias="createDate")
    created_by: Optional[StrictStr] = Field(default=None, description="The ID of the user who created the current user account.", alias="createdBy")
    spam: Optional[StrictBool] = Field(default=None, description="Specifies if tips, updates and offers are allowed to be sent to the user or not.")
    check_activation: Optional[StrictBool] = Field(default=None, alias="checkActivation")
    __properties: ClassVar[List[str]] = ["id", "firstName", "lastName", "userName", "birthDate", "sex", "status", "activationStatus", "terminatedDate", "title", "workFromDate", "email", "contacts", "contactsList", "location", "notes", "removed", "lastModified", "tenantId", "isActive", "cultureName", "mobilePhone", "mobilePhoneActivationStatus", "sid", "ldapQouta", "ssoNameId", "ssoSessionId", "createDate", "createdBy", "spam", "checkActivation"]

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
        """Create an instance of UserInfo from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "is_active",
            "check_activation",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
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

        # set to None if birth_date (nullable) is None
        # and model_fields_set contains the field
        if self.birth_date is None and "birth_date" in self.model_fields_set:
            _dict['birthDate'] = None

        # set to None if sex (nullable) is None
        # and model_fields_set contains the field
        if self.sex is None and "sex" in self.model_fields_set:
            _dict['sex'] = None

        # set to None if terminated_date (nullable) is None
        # and model_fields_set contains the field
        if self.terminated_date is None and "terminated_date" in self.model_fields_set:
            _dict['terminatedDate'] = None

        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if work_from_date (nullable) is None
        # and model_fields_set contains the field
        if self.work_from_date is None and "work_from_date" in self.model_fields_set:
            _dict['workFromDate'] = None

        # set to None if email (nullable) is None
        # and model_fields_set contains the field
        if self.email is None and "email" in self.model_fields_set:
            _dict['email'] = None

        # set to None if contacts (nullable) is None
        # and model_fields_set contains the field
        if self.contacts is None and "contacts" in self.model_fields_set:
            _dict['contacts'] = None

        # set to None if contacts_list (nullable) is None
        # and model_fields_set contains the field
        if self.contacts_list is None and "contacts_list" in self.model_fields_set:
            _dict['contactsList'] = None

        # set to None if location (nullable) is None
        # and model_fields_set contains the field
        if self.location is None and "location" in self.model_fields_set:
            _dict['location'] = None

        # set to None if notes (nullable) is None
        # and model_fields_set contains the field
        if self.notes is None and "notes" in self.model_fields_set:
            _dict['notes'] = None

        # set to None if culture_name (nullable) is None
        # and model_fields_set contains the field
        if self.culture_name is None and "culture_name" in self.model_fields_set:
            _dict['cultureName'] = None

        # set to None if mobile_phone (nullable) is None
        # and model_fields_set contains the field
        if self.mobile_phone is None and "mobile_phone" in self.model_fields_set:
            _dict['mobilePhone'] = None

        # set to None if sid (nullable) is None
        # and model_fields_set contains the field
        if self.sid is None and "sid" in self.model_fields_set:
            _dict['sid'] = None

        # set to None if sso_name_id (nullable) is None
        # and model_fields_set contains the field
        if self.sso_name_id is None and "sso_name_id" in self.model_fields_set:
            _dict['ssoNameId'] = None

        # set to None if sso_session_id (nullable) is None
        # and model_fields_set contains the field
        if self.sso_session_id is None and "sso_session_id" in self.model_fields_set:
            _dict['ssoSessionId'] = None

        # set to None if created_by (nullable) is None
        # and model_fields_set contains the field
        if self.created_by is None and "created_by" in self.model_fields_set:
            _dict['createdBy'] = None

        # set to None if spam (nullable) is None
        # and model_fields_set contains the field
        if self.spam is None and "spam" in self.model_fields_set:
            _dict['spam'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UserInfo from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "firstName": obj.get("firstName"),
            "lastName": obj.get("lastName"),
            "userName": obj.get("userName"),
            "birthDate": obj.get("birthDate"),
            "sex": obj.get("sex"),
            "status": obj.get("status"),
            "activationStatus": obj.get("activationStatus"),
            "terminatedDate": obj.get("terminatedDate"),
            "title": obj.get("title"),
            "workFromDate": obj.get("workFromDate"),
            "email": obj.get("email"),
            "contacts": obj.get("contacts"),
            "contactsList": obj.get("contactsList"),
            "location": obj.get("location"),
            "notes": obj.get("notes"),
            "removed": obj.get("removed"),
            "lastModified": obj.get("lastModified"),
            "tenantId": obj.get("tenantId"),
            "isActive": obj.get("isActive"),
            "cultureName": obj.get("cultureName"),
            "mobilePhone": obj.get("mobilePhone"),
            "mobilePhoneActivationStatus": obj.get("mobilePhoneActivationStatus"),
            "sid": obj.get("sid"),
            "ldapQouta": obj.get("ldapQouta"),
            "ssoNameId": obj.get("ssoNameId"),
            "ssoSessionId": obj.get("ssoSessionId"),
            "createDate": obj.get("createDate"),
            "createdBy": obj.get("createdBy"),
            "spam": obj.get("spam"),
            "checkActivation": obj.get("checkActivation")
        })
        return _obj


