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
from docspace_api_sdk.models.edit_history_url import EditHistoryUrl
from typing import Optional, Set
from typing_extensions import Self

class EditHistoryDataDto(BaseModel):
    """
    The file editing history data.
    """ # noqa: E501
    changes_url: Optional[StrictStr] = Field(default=None, description="The URL address of the file with the document changes data.", alias="changesUrl")
    key: Optional[StrictStr] = Field(description="The document identifier used to unambiguously identify the document file.")
    previous: Optional[EditHistoryUrl] = None
    token: Optional[StrictStr] = Field(default=None, description="The encrypted signature added to the parameter in the form of a token.")
    url: Optional[StrictStr] = Field(description="The URL address of the current document version.")
    version: StrictInt = Field(description="The document version number.")
    file_type: Optional[StrictStr] = Field(description="The document extension.", alias="fileType")
    __properties: ClassVar[List[str]] = ["changesUrl", "key", "previous", "token", "url", "version", "fileType"]

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
        """Create an instance of EditHistoryDataDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of previous
        if self.previous:
            _dict['previous'] = self.previous.to_dict()
        # set to None if changes_url (nullable) is None
        # and model_fields_set contains the field
        if self.changes_url is None and "changes_url" in self.model_fields_set:
            _dict['changesUrl'] = None

        # set to None if key (nullable) is None
        # and model_fields_set contains the field
        if self.key is None and "key" in self.model_fields_set:
            _dict['key'] = None

        # set to None if token (nullable) is None
        # and model_fields_set contains the field
        if self.token is None and "token" in self.model_fields_set:
            _dict['token'] = None

        # set to None if url (nullable) is None
        # and model_fields_set contains the field
        if self.url is None and "url" in self.model_fields_set:
            _dict['url'] = None

        # set to None if file_type (nullable) is None
        # and model_fields_set contains the field
        if self.file_type is None and "file_type" in self.model_fields_set:
            _dict['fileType'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EditHistoryDataDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "changesUrl": obj.get("changesUrl"),
            "key": obj.get("key"),
            "previous": EditHistoryUrl.from_dict(obj["previous"]) if obj.get("previous") is not None else None,
            "token": obj.get("token"),
            "url": obj.get("url"),
            "version": obj.get("version"),
            "fileType": obj.get("fileType")
        })
        return _obj


