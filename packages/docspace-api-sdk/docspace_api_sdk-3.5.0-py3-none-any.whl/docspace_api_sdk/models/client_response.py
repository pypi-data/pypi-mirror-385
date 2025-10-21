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
from typing import Optional, Set
from typing_extensions import Self

class ClientResponse(BaseModel):
    """
    ClientResponse
    """ # noqa: E501
    name: Optional[StrictStr] = Field(default=None, description="The client name.")
    description: Optional[StrictStr] = Field(default=None, description="The client description.")
    tenant: Optional[StrictInt] = Field(default=None, description="The tenant ID associated with the client.")
    scopes: Optional[List[StrictStr]] = Field(default=None, description="The client scopes.")
    enabled: Optional[StrictBool] = Field(default=None, description="Specifies if the client is currently enabled or not.")
    client_id: Optional[StrictStr] = Field(default=None, description="The client identifier issued to the client during registration.")
    client_secret: Optional[StrictStr] = Field(default=None, description="The client secret issued to the client during registration.")
    website_url: Optional[StrictStr] = Field(default=None, description="The URL to the client's website.")
    terms_url: Optional[StrictStr] = Field(default=None, description="The URL to the client's terms of service.")
    policy_url: Optional[StrictStr] = Field(default=None, description="The URL to the client's privacy policy.")
    logo: Optional[StrictStr] = Field(default=None, description="The URL to the client's logo.")
    authentication_methods: Optional[List[StrictStr]] = Field(default=None, description="The authentication methods supported by the client.")
    redirect_uris: Optional[List[StrictStr]] = Field(default=None, description="The list of allowed redirect URIs.")
    allowed_origins: Optional[List[StrictStr]] = Field(default=None, description="The list of allowed CORS origins.")
    logout_redirect_uris: Optional[List[StrictStr]] = Field(default=None, description="The list of allowed logout redirect URIs.")
    created_on: Optional[datetime] = Field(default=None, description="The date and time when the client was created.")
    created_by: Optional[StrictStr] = Field(default=None, description="The user who created the client.")
    modified_on: Optional[datetime] = Field(default=None, description="The date and time when the client was last modified.")
    modified_by: Optional[StrictStr] = Field(default=None, description="The user who last modified the client.")
    is_public: Optional[StrictBool] = Field(default=None, description="Indicates whether the client is accessible by third-party tenants.")
    __properties: ClassVar[List[str]] = ["name", "description", "tenant", "scopes", "enabled", "client_id", "client_secret", "website_url", "terms_url", "policy_url", "logo", "authentication_methods", "redirect_uris", "allowed_origins", "logout_redirect_uris", "created_on", "created_by", "modified_on", "modified_by", "is_public"]

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
        """Create an instance of ClientResponse from a JSON string"""
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
        """Create an instance of ClientResponse from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "description": obj.get("description"),
            "tenant": obj.get("tenant"),
            "scopes": obj.get("scopes"),
            "enabled": obj.get("enabled"),
            "client_id": obj.get("client_id"),
            "client_secret": obj.get("client_secret"),
            "website_url": obj.get("website_url"),
            "terms_url": obj.get("terms_url"),
            "policy_url": obj.get("policy_url"),
            "logo": obj.get("logo"),
            "authentication_methods": obj.get("authentication_methods"),
            "redirect_uris": obj.get("redirect_uris"),
            "allowed_origins": obj.get("allowed_origins"),
            "logout_redirect_uris": obj.get("logout_redirect_uris"),
            "created_on": obj.get("created_on"),
            "created_by": obj.get("created_by"),
            "modified_on": obj.get("modified_on"),
            "modified_by": obj.get("modified_by"),
            "is_public": obj.get("is_public")
        })
        return _obj


