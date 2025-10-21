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
from docspace_api_sdk.models.action_type import ActionType
from docspace_api_sdk.models.api_date_time import ApiDateTime
from docspace_api_sdk.models.entry_type import EntryType
from docspace_api_sdk.models.location_type import LocationType
from docspace_api_sdk.models.message_action import MessageAction
from docspace_api_sdk.models.product_type import ProductType
from typing import Optional, Set
from typing_extensions import Self

class AuditEventDto(BaseModel):
    """
    The audit event parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The audit event ID.")
    var_date: Optional[ApiDateTime] = Field(default=None, alias="date")
    user: Optional[StrictStr] = Field(default=None, description="The name of the user who triggered the audit event.")
    user_id: Optional[StrictStr] = Field(default=None, description="The ID of the user who triggered the audit event.", alias="userId")
    action: Optional[StrictStr] = Field(default=None, description="The audit event action.")
    action_id: Optional[MessageAction] = Field(default=None, alias="actionId")
    ip: Optional[StrictStr] = Field(default=None, description="The audit event IP.")
    country: Optional[StrictStr] = Field(default=None, description="The audit event country.")
    city: Optional[StrictStr] = Field(default=None, description="The audit event city.")
    browser: Optional[StrictStr] = Field(default=None, description="The audit event browser.")
    platform: Optional[StrictStr] = Field(default=None, description="The audit event platform.")
    page: Optional[StrictStr] = Field(default=None, description="The audit event page.")
    action_type: Optional[ActionType] = Field(default=None, alias="actionType")
    product: Optional[ProductType] = None
    location: Optional[LocationType] = None
    target: Optional[List[StrictStr]] = Field(default=None, description="The list of target objects affected by the audit event (e.g., document ID, user account).")
    entries: Optional[List[EntryType]] = Field(default=None, description="The list of audit entry types (e.g., Folder, User, File).")
    context: Optional[StrictStr] = Field(default=None, description="The audit event context.")
    __properties: ClassVar[List[str]] = ["id", "date", "user", "userId", "action", "actionId", "ip", "country", "city", "browser", "platform", "page", "actionType", "product", "location", "target", "entries", "context"]

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
        """Create an instance of AuditEventDto from a JSON string"""
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

        # set to None if target (nullable) is None
        # and model_fields_set contains the field
        if self.target is None and "target" in self.model_fields_set:
            _dict['target'] = None

        # set to None if entries (nullable) is None
        # and model_fields_set contains the field
        if self.entries is None and "entries" in self.model_fields_set:
            _dict['entries'] = None

        # set to None if context (nullable) is None
        # and model_fields_set contains the field
        if self.context is None and "context" in self.model_fields_set:
            _dict['context'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AuditEventDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "date": ApiDateTime.from_dict(obj["date"]) if obj.get("date") is not None else None,
            "user": obj.get("user"),
            "userId": obj.get("userId"),
            "action": obj.get("action"),
            "actionId": obj.get("actionId"),
            "ip": obj.get("ip"),
            "country": obj.get("country"),
            "city": obj.get("city"),
            "browser": obj.get("browser"),
            "platform": obj.get("platform"),
            "page": obj.get("page"),
            "actionType": obj.get("actionType"),
            "product": obj.get("product"),
            "location": obj.get("location"),
            "target": obj.get("target"),
            "entries": obj.get("entries"),
            "context": obj.get("context")
        })
        return _obj


