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

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.edit_history_author import EditHistoryAuthor
from docspace_api_sdk.models.edit_history_changes_wrapper import EditHistoryChangesWrapper
from typing import Optional, Set
from typing_extensions import Self

class EditHistoryDto(BaseModel):
    """
    The file editing history parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The document ID.")
    key: Optional[StrictStr] = Field(default=None, description="The document identifier used to unambiguously identify the document file.")
    version: Optional[StrictInt] = Field(default=None, description="The document version number.")
    version_group: Optional[StrictInt] = Field(default=None, description="The document version group.", alias="versionGroup")
    user: Optional[EditHistoryAuthor] = None
    created: Optional[ApiDateTime] = None
    changes_history: Optional[StrictStr] = Field(default=None, description="The file history changes in the string format.", alias="changesHistory")
    changes: Optional[List[EditHistoryChangesWrapper]] = Field(default=None, description="The list of file history changes.")
    server_version: Optional[StrictStr] = Field(default=None, description="The current server version number.", alias="serverVersion")
    __properties: ClassVar[List[str]] = ["id", "key", "version", "versionGroup", "user", "created", "changesHistory", "changes", "serverVersion"]

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
        """Create an instance of EditHistoryDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict['user'] = self.user.to_dict()
        # override the default output from pydantic by calling `to_dict()` of created
        if self.created:
            _dict['created'] = self.created.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in changes (list)
        _items = []
        if self.changes:
            for _item_changes in self.changes:
                if _item_changes:
                    _items.append(_item_changes.to_dict())
            _dict['changes'] = _items
        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if changes_history (nullable) is None
        # and model_fields_set contains the field
        if self.changes_history is None and "changes_history" in self.model_fields_set:
            _dict['changesHistory'] = None

        # set to None if changes (nullable) is None
        # and model_fields_set contains the field
        if self.changes is None and "changes" in self.model_fields_set:
            _dict['changes'] = None

        # set to None if server_version (nullable) is None
        # and model_fields_set contains the field
        if self.server_version is None and "server_version" in self.model_fields_set:
            _dict['serverVersion'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EditHistoryDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "key": obj.get("key"),
            "version": obj.get("version"),
            "versionGroup": obj.get("versionGroup"),
            "user": EditHistoryAuthor.from_dict(obj["user"]) if obj.get("user") is not None else None,
            "created": ApiDateTime.from_dict(obj["created"]) if obj.get("created") is not None else None,
            "changesHistory": obj.get("changesHistory"),
            "changes": [EditHistoryChangesWrapper.from_dict(_item) for _item in obj["changes"]] if obj.get("changes") is not None else None,
            "serverVersion": obj.get("serverVersion")
        })
        return _obj


