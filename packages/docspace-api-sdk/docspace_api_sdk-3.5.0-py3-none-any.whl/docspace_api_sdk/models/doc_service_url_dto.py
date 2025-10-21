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
from typing import Optional, Set
from typing_extensions import Self

class DocServiceUrlDto(BaseModel):
    """
    The document service URL parameters.
    """ # noqa: E501
    version: Optional[StrictStr] = Field(description="The version of the document service.")
    doc_service_url_api: Optional[StrictStr] = Field(description="The document service URL API.", alias="docServiceUrlApi")
    doc_service_url: Optional[StrictStr] = Field(description="The document service URL.", alias="docServiceUrl")
    doc_service_preload_url: Optional[StrictStr] = Field(description="The URL used to preload the document service scripts.", alias="docServicePreloadUrl")
    doc_service_url_internal: Optional[StrictStr] = Field(description="The internal document service URL.", alias="docServiceUrlInternal")
    doc_service_portal_url: Optional[StrictStr] = Field(description="The document service portal URL.", alias="docServicePortalUrl")
    doc_service_signature_header: Optional[StrictStr] = Field(description="The document service signature header.", alias="docServiceSignatureHeader")
    doc_service_ssl_verification: StrictBool = Field(description="Specifies if the document service SSL verification is enabled.", alias="docServiceSslVerification")
    is_default: StrictBool = Field(description="Specifies if the document service is default.", alias="isDefault")
    __properties: ClassVar[List[str]] = ["version", "docServiceUrlApi", "docServiceUrl", "docServicePreloadUrl", "docServiceUrlInternal", "docServicePortalUrl", "docServiceSignatureHeader", "docServiceSslVerification", "isDefault"]

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
        """Create an instance of DocServiceUrlDto from a JSON string"""
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
        # set to None if version (nullable) is None
        # and model_fields_set contains the field
        if self.version is None and "version" in self.model_fields_set:
            _dict['version'] = None

        # set to None if doc_service_url_api (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_url_api is None and "doc_service_url_api" in self.model_fields_set:
            _dict['docServiceUrlApi'] = None

        # set to None if doc_service_url (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_url is None and "doc_service_url" in self.model_fields_set:
            _dict['docServiceUrl'] = None

        # set to None if doc_service_preload_url (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_preload_url is None and "doc_service_preload_url" in self.model_fields_set:
            _dict['docServicePreloadUrl'] = None

        # set to None if doc_service_url_internal (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_url_internal is None and "doc_service_url_internal" in self.model_fields_set:
            _dict['docServiceUrlInternal'] = None

        # set to None if doc_service_portal_url (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_portal_url is None and "doc_service_portal_url" in self.model_fields_set:
            _dict['docServicePortalUrl'] = None

        # set to None if doc_service_signature_header (nullable) is None
        # and model_fields_set contains the field
        if self.doc_service_signature_header is None and "doc_service_signature_header" in self.model_fields_set:
            _dict['docServiceSignatureHeader'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DocServiceUrlDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "version": obj.get("version"),
            "docServiceUrlApi": obj.get("docServiceUrlApi"),
            "docServiceUrl": obj.get("docServiceUrl"),
            "docServicePreloadUrl": obj.get("docServicePreloadUrl"),
            "docServiceUrlInternal": obj.get("docServiceUrlInternal"),
            "docServicePortalUrl": obj.get("docServicePortalUrl"),
            "docServiceSignatureHeader": obj.get("docServiceSignatureHeader"),
            "docServiceSslVerification": obj.get("docServiceSslVerification"),
            "isDefault": obj.get("isDefault")
        })
        return _obj


