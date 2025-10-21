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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class FirebaseDto(BaseModel):
    """
    The Firebase parameters.
    """ # noqa: E501
    api_key: Optional[StrictStr] = Field(description="The Firebase API key.", alias="apiKey")
    auth_domain: Optional[StrictStr] = Field(description="The Firebase authentication domain.", alias="authDomain")
    project_id: Optional[StrictStr] = Field(description="The Firebase project ID.", alias="projectId")
    storage_bucket: Optional[StrictStr] = Field(description="The Firebase storage bucket.", alias="storageBucket")
    messaging_sender_id: Optional[StrictStr] = Field(description="The Firebase messaging sender ID.", alias="messagingSenderId")
    app_id: Optional[StrictStr] = Field(description="The Firebase application ID.", alias="appId")
    measurement_id: Optional[StrictStr] = Field(description="The Firebase measurement ID.", alias="measurementId")
    database_url: Optional[StrictStr] = Field(description="The Firebase database URL.", alias="databaseURL")
    __properties: ClassVar[List[str]] = ["apiKey", "authDomain", "projectId", "storageBucket", "messagingSenderId", "appId", "measurementId", "databaseURL"]

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
        """Create an instance of FirebaseDto from a JSON string"""
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
        # set to None if api_key (nullable) is None
        # and model_fields_set contains the field
        if self.api_key is None and "api_key" in self.model_fields_set:
            _dict['apiKey'] = None

        # set to None if auth_domain (nullable) is None
        # and model_fields_set contains the field
        if self.auth_domain is None and "auth_domain" in self.model_fields_set:
            _dict['authDomain'] = None

        # set to None if project_id (nullable) is None
        # and model_fields_set contains the field
        if self.project_id is None and "project_id" in self.model_fields_set:
            _dict['projectId'] = None

        # set to None if storage_bucket (nullable) is None
        # and model_fields_set contains the field
        if self.storage_bucket is None and "storage_bucket" in self.model_fields_set:
            _dict['storageBucket'] = None

        # set to None if messaging_sender_id (nullable) is None
        # and model_fields_set contains the field
        if self.messaging_sender_id is None and "messaging_sender_id" in self.model_fields_set:
            _dict['messagingSenderId'] = None

        # set to None if app_id (nullable) is None
        # and model_fields_set contains the field
        if self.app_id is None and "app_id" in self.model_fields_set:
            _dict['appId'] = None

        # set to None if measurement_id (nullable) is None
        # and model_fields_set contains the field
        if self.measurement_id is None and "measurement_id" in self.model_fields_set:
            _dict['measurementId'] = None

        # set to None if database_url (nullable) is None
        # and model_fields_set contains the field
        if self.database_url is None and "database_url" in self.model_fields_set:
            _dict['databaseURL'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FirebaseDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "apiKey": obj.get("apiKey"),
            "authDomain": obj.get("authDomain"),
            "projectId": obj.get("projectId"),
            "storageBucket": obj.get("storageBucket"),
            "messagingSenderId": obj.get("messagingSenderId"),
            "appId": obj.get("appId"),
            "measurementId": obj.get("measurementId"),
            "databaseURL": obj.get("databaseURL")
        })
        return _obj


