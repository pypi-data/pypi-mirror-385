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
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.webhook_trigger import WebhookTrigger
from typing import Optional, Set
from typing_extensions import Self

class WebhooksLogDto(BaseModel):
    """
    The webhook log parameters.
    """ # noqa: E501
    id: StrictInt = Field(description="The webhook log ID.")
    config_name: Optional[StrictStr] = Field(default=None, description="The webhook configuration name.", alias="configName")
    trigger: Optional[WebhookTrigger] = None
    creation_time: Optional[datetime] = Field(default=None, description="The webhook creation time.", alias="creationTime")
    method: Optional[StrictStr] = Field(default=None, description="The webhook method.")
    route: Optional[StrictStr] = Field(default=None, description="The webhook route.")
    request_headers: Optional[StrictStr] = Field(default=None, description="The webhook request headers.", alias="requestHeaders")
    request_payload: Optional[StrictStr] = Field(default=None, description="The webhook request payload.", alias="requestPayload")
    response_headers: Optional[StrictStr] = Field(default=None, description="The webhook response headers.", alias="responseHeaders")
    response_payload: Optional[StrictStr] = Field(default=None, description="The webhook response payload.", alias="responsePayload")
    status: Optional[StrictInt] = Field(default=None, description="The webhook status.")
    delivery: Optional[datetime] = Field(default=None, description="The webhook delivery time.")
    __properties: ClassVar[List[str]] = ["id", "configName", "trigger", "creationTime", "method", "route", "requestHeaders", "requestPayload", "responseHeaders", "responsePayload", "status", "delivery"]

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
        """Create an instance of WebhooksLogDto from a JSON string"""
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
        # set to None if config_name (nullable) is None
        # and model_fields_set contains the field
        if self.config_name is None and "config_name" in self.model_fields_set:
            _dict['configName'] = None

        # set to None if method (nullable) is None
        # and model_fields_set contains the field
        if self.method is None and "method" in self.model_fields_set:
            _dict['method'] = None

        # set to None if route (nullable) is None
        # and model_fields_set contains the field
        if self.route is None and "route" in self.model_fields_set:
            _dict['route'] = None

        # set to None if request_headers (nullable) is None
        # and model_fields_set contains the field
        if self.request_headers is None and "request_headers" in self.model_fields_set:
            _dict['requestHeaders'] = None

        # set to None if request_payload (nullable) is None
        # and model_fields_set contains the field
        if self.request_payload is None and "request_payload" in self.model_fields_set:
            _dict['requestPayload'] = None

        # set to None if response_headers (nullable) is None
        # and model_fields_set contains the field
        if self.response_headers is None and "response_headers" in self.model_fields_set:
            _dict['responseHeaders'] = None

        # set to None if response_payload (nullable) is None
        # and model_fields_set contains the field
        if self.response_payload is None and "response_payload" in self.model_fields_set:
            _dict['responsePayload'] = None

        # set to None if delivery (nullable) is None
        # and model_fields_set contains the field
        if self.delivery is None and "delivery" in self.model_fields_set:
            _dict['delivery'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of WebhooksLogDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "configName": obj.get("configName"),
            "trigger": obj.get("trigger"),
            "creationTime": obj.get("creationTime"),
            "method": obj.get("method"),
            "route": obj.get("route"),
            "requestHeaders": obj.get("requestHeaders"),
            "requestPayload": obj.get("requestPayload"),
            "responseHeaders": obj.get("responseHeaders"),
            "responsePayload": obj.get("responsePayload"),
            "status": obj.get("status"),
            "delivery": obj.get("delivery")
        })
        return _obj


