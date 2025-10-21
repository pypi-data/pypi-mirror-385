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
from docspace_api_sdk.models.message_action import MessageAction
from typing import Optional, Set
from typing_extensions import Self

class LoginEventDto(BaseModel):
    """
    The login event parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The login event ID.")
    var_date: Optional[ApiDateTime] = Field(default=None, alias="date")
    user: Optional[StrictStr] = Field(default=None, description="The user name of the login event.")
    user_id: Optional[StrictStr] = Field(default=None, description="The user ID of the login event.", alias="userId")
    login: Optional[StrictStr] = Field(default=None, description="The user login of the login event.")
    action: Optional[StrictStr] = Field(default=None, description="The login event action.")
    action_id: Optional[MessageAction] = Field(default=None, alias="actionId")
    ip: Optional[StrictStr] = Field(default=None, description="The login event IP.")
    country: Optional[StrictStr] = Field(default=None, description="The login event country.")
    city: Optional[StrictStr] = Field(default=None, description="The login event city.")
    browser: Optional[StrictStr] = Field(default=None, description="The login event browser.")
    platform: Optional[StrictStr] = Field(default=None, description="The login event platform.")
    page: Optional[StrictStr] = Field(default=None, description="The login event page.")
    __properties: ClassVar[List[str]] = ["id", "date", "user", "userId", "login", "action", "actionId", "ip", "country", "city", "browser", "platform", "page"]

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
        """Create an instance of LoginEventDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of var_date
        if self.var_date:
            _dict['date'] = self.var_date.to_dict()
        # set to None if user (nullable) is None
        # and model_fields_set contains the field
        if self.user is None and "user" in self.model_fields_set:
            _dict['user'] = None

        # set to None if login (nullable) is None
        # and model_fields_set contains the field
        if self.login is None and "login" in self.model_fields_set:
            _dict['login'] = None

        # set to None if action (nullable) is None
        # and model_fields_set contains the field
        if self.action is None and "action" in self.model_fields_set:
            _dict['action'] = None

        # set to None if ip (nullable) is None
        # and model_fields_set contains the field
        if self.ip is None and "ip" in self.model_fields_set:
            _dict['ip'] = None

        # set to None if country (nullable) is None
        # and model_fields_set contains the field
        if self.country is None and "country" in self.model_fields_set:
            _dict['country'] = None

        # set to None if city (nullable) is None
        # and model_fields_set contains the field
        if self.city is None and "city" in self.model_fields_set:
            _dict['city'] = None

        # set to None if browser (nullable) is None
        # and model_fields_set contains the field
        if self.browser is None and "browser" in self.model_fields_set:
            _dict['browser'] = None

        # set to None if platform (nullable) is None
        # and model_fields_set contains the field
        if self.platform is None and "platform" in self.model_fields_set:
            _dict['platform'] = None

        # set to None if page (nullable) is None
        # and model_fields_set contains the field
        if self.page is None and "page" in self.model_fields_set:
            _dict['page'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of LoginEventDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "date": ApiDateTime.from_dict(obj["date"]) if obj.get("date") is not None else None,
            "user": obj.get("user"),
            "userId": obj.get("userId"),
            "login": obj.get("login"),
            "action": obj.get("action"),
            "actionId": obj.get("actionId"),
            "ip": obj.get("ip"),
            "country": obj.get("country"),
            "city": obj.get("city"),
            "browser": obj.get("browser"),
            "platform": obj.get("platform"),
            "page": obj.get("page")
        })
        return _obj


