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
from typing_extensions import Annotated
from docspace_api_sdk.models.webhook_trigger import WebhookTrigger
from typing import Optional, Set
from typing_extensions import Self

class CreateWebhooksConfigRequestsDto(BaseModel):
    """
    The request parameters for creating the webhook configuration.
    """ # noqa: E501
    name: Annotated[str, Field(min_length=0, strict=True, max_length=50)] = Field(description="The human-readable name of the webhook configuration.")
    uri: Annotated[str, Field(min_length=1, strict=True)] = Field(description="The destination URL where the webhook events will be sent.")
    secret_key: Optional[Annotated[str, Field(min_length=0, strict=True, max_length=50)]] = Field(default=None, description="The webhook secret key used to sign the webhook payloads for the security verification.", alias="secretKey")
    enabled: Optional[StrictBool] = Field(default=None, description="Specifies whether the webhook configuration is active or not.")
    ssl: Optional[StrictBool] = Field(default=None, description="Specifies whether the SSL certificate verification is required or not.")
    triggers: Optional[WebhookTrigger] = None
    target_id: Optional[StrictStr] = Field(default=None, description="Target ID", alias="targetId")
    __properties: ClassVar[List[str]] = ["name", "uri", "secretKey", "enabled", "ssl", "triggers", "targetId"]

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
        """Create an instance of CreateWebhooksConfigRequestsDto from a JSON string"""
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
        # set to None if secret_key (nullable) is None
        # and model_fields_set contains the field
        if self.secret_key is None and "secret_key" in self.model_fields_set:
            _dict['secretKey'] = None

        # set to None if target_id (nullable) is None
        # and model_fields_set contains the field
        if self.target_id is None and "target_id" in self.model_fields_set:
            _dict['targetId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CreateWebhooksConfigRequestsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name"),
            "uri": obj.get("uri"),
            "secretKey": obj.get("secretKey"),
            "enabled": obj.get("enabled"),
            "ssl": obj.get("ssl"),
            "triggers": obj.get("triggers"),
            "targetId": obj.get("targetId")
        })
        return _obj


