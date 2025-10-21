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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Union, Any, List, Set, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal, Self
from pydantic import Field
from docspace_api_sdk.models.importable_api_entity import ImportableApiEntity

class MigratingApiGroup(ImportableApiEntity):
    """
    MigratingApiGroup
    """

    group_name: Optional[StrictStr] = Field(default=None, alias="groupName")
    module_name: Optional[StrictStr] = Field(default=None, alias="moduleName")
    user_uid_list: Optional[List[StrictStr]] = Field(default=None, alias="userUidList")

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
        """Create an instance of MigratingApiGroup from a JSON string"""
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
        # set to None if group_name (nullable) is None
        # and model_fields_set contains the field
        if self.group_name is None and "group_name" in self.model_fields_set:
            _dict['groupName'] = None

        # set to None if module_name (nullable) is None
        # and model_fields_set contains the field
        if self.module_name is None and "module_name" in self.model_fields_set:
            _dict['moduleName'] = None

        # set to None if user_uid_list (nullable) is None
        # and model_fields_set contains the field
        if self.user_uid_list is None and "user_uid_list" in self.model_fields_set:
            _dict['userUidList'] = None

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
            "groupName": obj.get("groupName"),
            "moduleName": obj.get("moduleName"),
            "userUidList": obj.get("userUidList")
        })
        return cls(**base_obj.model_dump(), **extra_fields)

