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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.link_type import LinkType
from typing import Optional, Set
from typing_extensions import Self

class FileShareLink(BaseModel):
    """
    A shareable link for a file with its configuration and status.
    """ # noqa: E501
    id: Optional[StrictStr] = Field(default=None, description="The unique identifier of the shared link.")
    title: Optional[StrictStr] = Field(default=None, description="The title of the shared content.")
    share_link: Optional[StrictStr] = Field(default=None, description="The URL for accessing the shared content.", alias="shareLink")
    expiration_date: Optional[ApiDateTime] = Field(default=None, alias="expirationDate")
    link_type: Optional[LinkType] = Field(default=None, alias="linkType")
    password: Optional[StrictStr] = Field(default=None, description="The password protection for accessing the shared content.")
    deny_download: Optional[StrictBool] = Field(default=None, description="Indicates whether downloading of the shared content is prohibited.", alias="denyDownload")
    is_expired: Optional[StrictBool] = Field(default=None, description="Indicates whether the shared link has expired.", alias="isExpired")
    primary: Optional[StrictBool] = Field(default=None, description="Indicates whether this is the primary shared link.")
    internal: Optional[StrictBool] = Field(default=None, description="Indicates whether the link is for the internal sharing only.")
    request_token: Optional[StrictStr] = Field(default=None, description="The token for validating access requests.", alias="requestToken")
    __properties: ClassVar[List[str]] = ["id", "title", "shareLink", "expirationDate", "linkType", "password", "denyDownload", "isExpired", "primary", "internal", "requestToken"]

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
        """Create an instance of FileShareLink from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of expiration_date
        if self.expiration_date:
            _dict['expirationDate'] = self.expiration_date.to_dict()
        # set to None if title (nullable) is None
        # and model_fields_set contains the field
        if self.title is None and "title" in self.model_fields_set:
            _dict['title'] = None

        # set to None if share_link (nullable) is None
        # and model_fields_set contains the field
        if self.share_link is None and "share_link" in self.model_fields_set:
            _dict['shareLink'] = None

        # set to None if password (nullable) is None
        # and model_fields_set contains the field
        if self.password is None and "password" in self.model_fields_set:
            _dict['password'] = None

        # set to None if deny_download (nullable) is None
        # and model_fields_set contains the field
        if self.deny_download is None and "deny_download" in self.model_fields_set:
            _dict['denyDownload'] = None

        # set to None if is_expired (nullable) is None
        # and model_fields_set contains the field
        if self.is_expired is None and "is_expired" in self.model_fields_set:
            _dict['isExpired'] = None

        # set to None if internal (nullable) is None
        # and model_fields_set contains the field
        if self.internal is None and "internal" in self.model_fields_set:
            _dict['internal'] = None

        # set to None if request_token (nullable) is None
        # and model_fields_set contains the field
        if self.request_token is None and "request_token" in self.model_fields_set:
            _dict['requestToken'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FileShareLink from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "title": obj.get("title"),
            "shareLink": obj.get("shareLink"),
            "expirationDate": ApiDateTime.from_dict(obj["expirationDate"]) if obj.get("expirationDate") is not None else None,
            "linkType": obj.get("linkType"),
            "password": obj.get("password"),
            "denyDownload": obj.get("denyDownload"),
            "isExpired": obj.get("isExpired"),
            "primary": obj.get("primary"),
            "internal": obj.get("internal"),
            "requestToken": obj.get("requestToken")
        })
        return _obj


