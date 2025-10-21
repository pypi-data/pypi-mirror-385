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
from docspace_api_sdk.models.current_license_info import CurrentLicenseInfo
from typing import Optional, Set
from typing_extensions import Self

class PaymentSettingsDto(BaseModel):
    """
    The payment settings parameters.
    """ # noqa: E501
    sales_email: Optional[StrictStr] = Field(description="The email address for sales inquiries and support.", alias="salesEmail")
    feedback_and_support_url: Optional[StrictStr] = Field(default=None, description="The URL for accessing the feedback and support resources.", alias="feedbackAndSupportUrl")
    buy_url: Optional[StrictStr] = Field(description="The URL for purchasing or upgrading the product.", alias="buyUrl")
    standalone: StrictBool = Field(description="Indicates whether the system is running in standalone mode.")
    current_license: CurrentLicenseInfo = Field(alias="currentLicense")
    max: StrictInt = Field(description="The maximum quota quantity.")
    __properties: ClassVar[List[str]] = ["salesEmail", "feedbackAndSupportUrl", "buyUrl", "standalone", "currentLicense", "max"]

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
        """Create an instance of PaymentSettingsDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of current_license
        if self.current_license:
            _dict['currentLicense'] = self.current_license.to_dict()
        # set to None if sales_email (nullable) is None
        # and model_fields_set contains the field
        if self.sales_email is None and "sales_email" in self.model_fields_set:
            _dict['salesEmail'] = None

        # set to None if feedback_and_support_url (nullable) is None
        # and model_fields_set contains the field
        if self.feedback_and_support_url is None and "feedback_and_support_url" in self.model_fields_set:
            _dict['feedbackAndSupportUrl'] = None

        # set to None if buy_url (nullable) is None
        # and model_fields_set contains the field
        if self.buy_url is None and "buy_url" in self.model_fields_set:
            _dict['buyUrl'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PaymentSettingsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "salesEmail": obj.get("salesEmail"),
            "feedbackAndSupportUrl": obj.get("feedbackAndSupportUrl"),
            "buyUrl": obj.get("buyUrl"),
            "standalone": obj.get("standalone"),
            "currentLicense": CurrentLicenseInfo.from_dict(obj["currentLicense"]) if obj.get("currentLicense") is not None else None,
            "max": obj.get("max")
        })
        return _obj


