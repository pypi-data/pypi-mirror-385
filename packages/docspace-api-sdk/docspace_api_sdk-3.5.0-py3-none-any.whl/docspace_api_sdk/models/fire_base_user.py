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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from docspace_api_sdk.models.db_tenant import DbTenant
from typing import Optional, Set
from typing_extensions import Self

class FireBaseUser(BaseModel):
    """
    The Firebase user parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The Firebase user ID.")
    user_id: Optional[StrictStr] = Field(default=None, description="The user ID.", alias="userId")
    tenant_id: Optional[StrictInt] = Field(default=None, description="The tenant ID.", alias="tenantId")
    firebase_device_token: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The Firebase device token.", alias="firebaseDeviceToken")
    application: Optional[Annotated[str, Field(strict=True, max_length=20)]] = Field(default=None, description="The Firebase application.")
    is_subscribed: Optional[StrictBool] = Field(default=None, description="Specifies if the user is subscribed to the push notifications or not.", alias="isSubscribed")
    tenant: Optional[DbTenant] = None
    __properties: ClassVar[List[str]] = ["id", "userId", "tenantId", "firebaseDeviceToken", "application", "isSubscribed", "tenant"]

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
        """Create an instance of FireBaseUser from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of tenant
        if self.tenant:
            _dict['tenant'] = self.tenant.to_dict()
        # set to None if firebase_device_token (nullable) is None
        # and model_fields_set contains the field
        if self.firebase_device_token is None and "firebase_device_token" in self.model_fields_set:
            _dict['firebaseDeviceToken'] = None

        # set to None if application (nullable) is None
        # and model_fields_set contains the field
        if self.application is None and "application" in self.model_fields_set:
            _dict['application'] = None

        # set to None if is_subscribed (nullable) is None
        # and model_fields_set contains the field
        if self.is_subscribed is None and "is_subscribed" in self.model_fields_set:
            _dict['isSubscribed'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FireBaseUser from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "userId": obj.get("userId"),
            "tenantId": obj.get("tenantId"),
            "firebaseDeviceToken": obj.get("firebaseDeviceToken"),
            "application": obj.get("application"),
            "isSubscribed": obj.get("isSubscribed"),
            "tenant": DbTenant.from_dict(obj["tenant"]) if obj.get("tenant") is not None else None
        })
        return _obj


