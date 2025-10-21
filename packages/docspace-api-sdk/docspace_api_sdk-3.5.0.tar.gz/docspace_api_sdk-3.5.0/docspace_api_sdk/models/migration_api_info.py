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
from docspace_api_sdk.models.migrating_api_group import MigratingApiGroup
from docspace_api_sdk.models.migrating_api_user import MigratingApiUser
from typing import Optional, Set
from typing_extensions import Self

class MigrationApiInfo(BaseModel):
    """
    MigrationApiInfo
    """ # noqa: E501
    migrator_name: Optional[StrictStr] = Field(default=None, alias="migratorName")
    operation: Optional[StrictStr] = None
    failed_archives: Optional[List[StrictStr]] = Field(default=None, alias="failedArchives")
    users: Optional[List[MigratingApiUser]] = None
    without_email_users: Optional[List[MigratingApiUser]] = Field(default=None, alias="withoutEmailUsers")
    exist_users: Optional[List[MigratingApiUser]] = Field(default=None, alias="existUsers")
    groups: Optional[List[MigratingApiGroup]] = None
    import_personal_files: Optional[StrictBool] = Field(default=None, alias="importPersonalFiles")
    import_shared_files: Optional[StrictBool] = Field(default=None, alias="importSharedFiles")
    import_shared_folders: Optional[StrictBool] = Field(default=None, alias="importSharedFolders")
    import_common_files: Optional[StrictBool] = Field(default=None, alias="importCommonFiles")
    import_project_files: Optional[StrictBool] = Field(default=None, alias="importProjectFiles")
    import_groups: Optional[StrictBool] = Field(default=None, alias="importGroups")
    successed_users: Optional[StrictInt] = Field(default=None, alias="successedUsers")
    failed_users: Optional[StrictInt] = Field(default=None, alias="failedUsers")
    files: Optional[List[StrictStr]] = None
    errors: Optional[List[StrictStr]] = None
    __properties: ClassVar[List[str]] = ["migratorName", "operation", "failedArchives", "users", "withoutEmailUsers", "existUsers", "groups", "importPersonalFiles", "importSharedFiles", "importSharedFolders", "importCommonFiles", "importProjectFiles", "importGroups", "successedUsers", "failedUsers", "files", "errors"]

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
        """Create an instance of MigrationApiInfo from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in users (list)
        _items = []
        if self.users:
            for _item_users in self.users:
                if _item_users:
                    _items.append(_item_users.to_dict())
            _dict['users'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in without_email_users (list)
        _items = []
        if self.without_email_users:
            for _item_without_email_users in self.without_email_users:
                if _item_without_email_users:
                    _items.append(_item_without_email_users.to_dict())
            _dict['withoutEmailUsers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in exist_users (list)
        _items = []
        if self.exist_users:
            for _item_exist_users in self.exist_users:
                if _item_exist_users:
                    _items.append(_item_exist_users.to_dict())
            _dict['existUsers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in groups (list)
        _items = []
        if self.groups:
            for _item_groups in self.groups:
                if _item_groups:
                    _items.append(_item_groups.to_dict())
            _dict['groups'] = _items
        # set to None if migrator_name (nullable) is None
        # and model_fields_set contains the field
        if self.migrator_name is None and "migrator_name" in self.model_fields_set:
            _dict['migratorName'] = None

        # set to None if operation (nullable) is None
        # and model_fields_set contains the field
        if self.operation is None and "operation" in self.model_fields_set:
            _dict['operation'] = None

        # set to None if failed_archives (nullable) is None
        # and model_fields_set contains the field
        if self.failed_archives is None and "failed_archives" in self.model_fields_set:
            _dict['failedArchives'] = None

        # set to None if users (nullable) is None
        # and model_fields_set contains the field
        if self.users is None and "users" in self.model_fields_set:
            _dict['users'] = None

        # set to None if without_email_users (nullable) is None
        # and model_fields_set contains the field
        if self.without_email_users is None and "without_email_users" in self.model_fields_set:
            _dict['withoutEmailUsers'] = None

        # set to None if exist_users (nullable) is None
        # and model_fields_set contains the field
        if self.exist_users is None and "exist_users" in self.model_fields_set:
            _dict['existUsers'] = None

        # set to None if groups (nullable) is None
        # and model_fields_set contains the field
        if self.groups is None and "groups" in self.model_fields_set:
            _dict['groups'] = None

        # set to None if files (nullable) is None
        # and model_fields_set contains the field
        if self.files is None and "files" in self.model_fields_set:
            _dict['files'] = None

        # set to None if errors (nullable) is None
        # and model_fields_set contains the field
        if self.errors is None and "errors" in self.model_fields_set:
            _dict['errors'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MigrationApiInfo from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "migratorName": obj.get("migratorName"),
            "operation": obj.get("operation"),
            "failedArchives": obj.get("failedArchives"),
            "users": [MigratingApiUser.from_dict(_item) for _item in obj["users"]] if obj.get("users") is not None else None,
            "withoutEmailUsers": [MigratingApiUser.from_dict(_item) for _item in obj["withoutEmailUsers"]] if obj.get("withoutEmailUsers") is not None else None,
            "existUsers": [MigratingApiUser.from_dict(_item) for _item in obj["existUsers"]] if obj.get("existUsers") is not None else None,
            "groups": [MigratingApiGroup.from_dict(_item) for _item in obj["groups"]] if obj.get("groups") is not None else None,
            "importPersonalFiles": obj.get("importPersonalFiles"),
            "importSharedFiles": obj.get("importSharedFiles"),
            "importSharedFolders": obj.get("importSharedFolders"),
            "importCommonFiles": obj.get("importCommonFiles"),
            "importProjectFiles": obj.get("importProjectFiles"),
            "importGroups": obj.get("importGroups"),
            "successedUsers": obj.get("successedUsers"),
            "failedUsers": obj.get("failedUsers"),
            "files": obj.get("files"),
            "errors": obj.get("errors")
        })
        return _obj


