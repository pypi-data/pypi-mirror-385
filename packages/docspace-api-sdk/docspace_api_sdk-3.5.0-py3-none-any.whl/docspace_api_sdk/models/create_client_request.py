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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class CreateClientRequest(BaseModel):
    """
    The request parameters for creating a client.
    """ # noqa: E501
    name: Optional[Annotated[str, Field(min_length=3, strict=True, max_length=256)]] = Field(default=None, description="The client name.")
    description: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=255)]] = Field(default=None, description="The client description.")
    logo: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The client logo in base64 format.")
    scopes: Optional[Annotated[List[StrictStr], Field(min_length=1)]] = Field(default=None, description="The client scopes.")
    allow_pkce: Optional[StrictBool] = Field(default=None, description="Indicates whether PKCE is allowed for the client.")
    is_public: Optional[StrictBool] = Field(default=None, description="Indicates whether the client is accessible by third-party tenants.")
    website_url: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The URL to the client's website.")
    terms_url: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The URL to the client's terms of service.")
    policy_url: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The URL to the client's privacy policy.")
    redirect_uris: List[StrictStr] = Field(description="The list of allowed redirect URIs.")
    allowed_origins: List[StrictStr] = Field(description="The list of allowed CORS origins.")
    logout_redirect_uri: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The list of allowed logout redirect URIs.")
    __properties: ClassVar[List[str]] = ["name", "description", "logo", "scopes", "allow_pkce", "is_public", "website_url", "terms_url", "policy_url", "redirect_uris", "allowed_origins", "logout_redirect_uri"]

    @field_validator('logo')
    def logo_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^data:image\/(?:png|jpeg|jpg|svg\+xml);base64,.*.{1,}", value):
            raise ValueError(r"must validate the regular expression /^data:image\/(?:png|jpeg|jpg|svg\+xml);base64,.*.{1,}/")
        return value

    @field_validator('website_url')
    def website_url_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$", value):
            raise ValueError(r"must validate the regular expression /^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$/")
        return value

    @field_validator('terms_url')
    def terms_url_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$", value):
            raise ValueError(r"must validate the regular expression /^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$/")
        return value

    @field_validator('policy_url')
    def policy_url_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$", value):
            raise ValueError(r"must validate the regular expression /^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$/")
        return value

    @field_validator('logout_redirect_uri')
    def logout_redirect_uri_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=]*)?$", value):
            raise ValueError(r"must validate the regular expression /^(https?:\/\/)?(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|localhost|[a-zA-Z0-9-]+)(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$|^https?:\/\/(\d{1,3}\.){3}\d{1,3}(:\d+)?(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&'()*+,;=]*)?$/")
        return value

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
        """Create an instance of CreateClientRequest from a JSON string"""
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
        """Create an instance of CreateClientRequest from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "description": obj.get("description"),
            "logo": obj.get("logo"),
            "scopes": obj.get("scopes"),
            "allow_pkce": obj.get("allow_pkce"),
            "is_public": obj.get("is_public"),
            "website_url": obj.get("website_url"),
            "terms_url": obj.get("terms_url"),
            "policy_url": obj.get("policy_url"),
            "redirect_uris": obj.get("redirect_uris"),
            "allowed_origins": obj.get("allowed_origins"),
            "logout_redirect_uri": obj.get("logout_redirect_uri")
        })
        return _obj


