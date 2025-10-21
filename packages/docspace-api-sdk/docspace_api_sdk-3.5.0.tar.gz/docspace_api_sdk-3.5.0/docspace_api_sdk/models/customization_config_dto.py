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

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.anonymous_config_dto import AnonymousConfigDto
from docspace_api_sdk.models.customer_config_dto import CustomerConfigDto
from docspace_api_sdk.models.feedback_config import FeedbackConfig
from docspace_api_sdk.models.goback_config import GobackConfig
from docspace_api_sdk.models.logo_config_dto import LogoConfigDto
from docspace_api_sdk.models.review_config import ReviewConfig
from docspace_api_sdk.models.start_filling_form import StartFillingForm
from docspace_api_sdk.models.submit_form import SubmitForm
from typing import Optional, Set
from typing_extensions import Self

class CustomizationConfigDto(BaseModel):
    """
    The customization config parameters.
    """ # noqa: E501
    about: Optional[StrictBool] = Field(default=None, description="Specifies if the customization is about.")
    customer: Optional[CustomerConfigDto] = None
    anonymous: Optional[AnonymousConfigDto] = None
    feedback: Optional[FeedbackConfig] = None
    forcesave: Optional[StrictBool] = Field(default=None, description="Specifies if the customization should be force saved.")
    goback: Optional[GobackConfig] = None
    review: Optional[ReviewConfig] = None
    logo: Optional[LogoConfigDto] = None
    mention_share: Optional[StrictBool] = Field(default=None, description="Specifies if the share should be mentioned.", alias="mentionShare")
    submit_form: Optional[SubmitForm] = Field(default=None, alias="submitForm")
    start_filling_form: Optional[StartFillingForm] = Field(default=None, alias="startFillingForm")
    __properties: ClassVar[List[str]] = ["about", "customer", "anonymous", "feedback", "forcesave", "goback", "review", "logo", "mentionShare", "submitForm", "startFillingForm"]

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
        """Create an instance of CustomizationConfigDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of customer
        if self.customer:
            _dict['customer'] = self.customer.to_dict()
        # override the default output from pydantic by calling `to_dict()` of anonymous
        if self.anonymous:
            _dict['anonymous'] = self.anonymous.to_dict()
        # override the default output from pydantic by calling `to_dict()` of feedback
        if self.feedback:
            _dict['feedback'] = self.feedback.to_dict()
        # override the default output from pydantic by calling `to_dict()` of goback
        if self.goback:
            _dict['goback'] = self.goback.to_dict()
        # override the default output from pydantic by calling `to_dict()` of review
        if self.review:
            _dict['review'] = self.review.to_dict()
        # override the default output from pydantic by calling `to_dict()` of logo
        if self.logo:
            _dict['logo'] = self.logo.to_dict()
        # override the default output from pydantic by calling `to_dict()` of submit_form
        if self.submit_form:
            _dict['submitForm'] = self.submit_form.to_dict()
        # override the default output from pydantic by calling `to_dict()` of start_filling_form
        if self.start_filling_form:
            _dict['startFillingForm'] = self.start_filling_form.to_dict()
        # set to None if forcesave (nullable) is None
        # and model_fields_set contains the field
        if self.forcesave is None and "forcesave" in self.model_fields_set:
            _dict['forcesave'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CustomizationConfigDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "about": obj.get("about"),
            "customer": CustomerConfigDto.from_dict(obj["customer"]) if obj.get("customer") is not None else None,
            "anonymous": AnonymousConfigDto.from_dict(obj["anonymous"]) if obj.get("anonymous") is not None else None,
            "feedback": FeedbackConfig.from_dict(obj["feedback"]) if obj.get("feedback") is not None else None,
            "forcesave": obj.get("forcesave"),
            "goback": GobackConfig.from_dict(obj["goback"]) if obj.get("goback") is not None else None,
            "review": ReviewConfig.from_dict(obj["review"]) if obj.get("review") is not None else None,
            "logo": LogoConfigDto.from_dict(obj["logo"]) if obj.get("logo") is not None else None,
            "mentionShare": obj.get("mentionShare"),
            "submitForm": SubmitForm.from_dict(obj["submitForm"]) if obj.get("submitForm") is not None else None,
            "startFillingForm": StartFillingForm.from_dict(obj["startFillingForm"]) if obj.get("startFillingForm") is not None else None
        })
        return _obj


