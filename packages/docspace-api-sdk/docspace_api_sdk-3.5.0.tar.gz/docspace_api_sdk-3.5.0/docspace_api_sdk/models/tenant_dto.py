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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.tenant_industry import TenantIndustry
from docspace_api_sdk.models.tenant_status import TenantStatus
from docspace_api_sdk.models.tenant_trusted_domains_type import TenantTrustedDomainsType
from typing import Optional, Set
from typing_extensions import Self

class TenantDto(BaseModel):
    """
    The tenant parameters.
    """ # noqa: E501
    affiliate_id: Optional[StrictStr] = Field(default=None, description="The affiliate ID.", alias="affiliateId")
    tenant_alias: Optional[StrictStr] = Field(default=None, description="The tenant alias.", alias="tenantAlias")
    calls: Optional[StrictBool] = Field(default=None, description="Specifies if the calls are available for this tenant or not.")
    campaign: Optional[StrictStr] = Field(default=None, description="The tenant campaign.")
    creation_date_time: Optional[datetime] = Field(default=None, description="The tenant creation date and time.", alias="creationDateTime")
    hosted_region: Optional[StrictStr] = Field(default=None, description="The hosted region.", alias="hostedRegion")
    tenant_id: Optional[StrictInt] = Field(default=None, description="The tenant ID.", alias="tenantId")
    industry: Optional[TenantIndustry] = None
    language: Optional[StrictStr] = Field(default=None, description="The tenant language.")
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the tenant was last modified.", alias="lastModified")
    mapped_domain: Optional[StrictStr] = Field(default=None, description="The tenant mapped domain.", alias="mappedDomain")
    name: Optional[StrictStr] = Field(default=None, description="The tenant name.")
    owner_id: Optional[StrictStr] = Field(default=None, description="The tenant owner ID.", alias="ownerId")
    payment_id: Optional[StrictStr] = Field(default=None, description="The tenant payment ID.", alias="paymentId")
    spam: Optional[StrictBool] = Field(default=None, description="Specifies if the ONLYOFFICE newsletter is allowed or not.")
    status: Optional[TenantStatus] = None
    status_change_date: Optional[datetime] = Field(default=None, description="The date and time when the tenant status was changed.", alias="statusChangeDate")
    time_zone: Optional[StrictStr] = Field(default=None, description="The tenant time zone.", alias="timeZone")
    trusted_domains: Optional[List[StrictStr]] = Field(default=None, description="The list of tenant trusted domains.", alias="trustedDomains")
    trusted_domains_raw: Optional[StrictStr] = Field(default=None, description="The tenant trusted domains in the string format.", alias="trustedDomainsRaw")
    trusted_domains_type: Optional[TenantTrustedDomainsType] = Field(default=None, alias="trustedDomainsType")
    version: Optional[StrictInt] = Field(default=None, description="The tenant version")
    version_changed: Optional[datetime] = Field(default=None, description="The date and time when the tenant version was changed.", alias="versionChanged")
    region: Optional[StrictStr] = Field(default=None, description="The tenant AWS region.")
    __properties: ClassVar[List[str]] = ["affiliateId", "tenantAlias", "calls", "campaign", "creationDateTime", "hostedRegion", "tenantId", "industry", "language", "lastModified", "mappedDomain", "name", "ownerId", "paymentId", "spam", "status", "statusChangeDate", "timeZone", "trustedDomains", "trustedDomainsRaw", "trustedDomainsType", "version", "versionChanged", "region"]

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
        """Create an instance of TenantDto from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "creation_date_time",
            "tenant_id",
            "status_change_date",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if affiliate_id (nullable) is None
        # and model_fields_set contains the field
        if self.affiliate_id is None and "affiliate_id" in self.model_fields_set:
            _dict['affiliateId'] = None

        # set to None if tenant_alias (nullable) is None
        # and model_fields_set contains the field
        if self.tenant_alias is None and "tenant_alias" in self.model_fields_set:
            _dict['tenantAlias'] = None

        # set to None if campaign (nullable) is None
        # and model_fields_set contains the field
        if self.campaign is None and "campaign" in self.model_fields_set:
            _dict['campaign'] = None

        # set to None if hosted_region (nullable) is None
        # and model_fields_set contains the field
        if self.hosted_region is None and "hosted_region" in self.model_fields_set:
            _dict['hostedRegion'] = None

        # set to None if language (nullable) is None
        # and model_fields_set contains the field
        if self.language is None and "language" in self.model_fields_set:
            _dict['language'] = None

        # set to None if mapped_domain (nullable) is None
        # and model_fields_set contains the field
        if self.mapped_domain is None and "mapped_domain" in self.model_fields_set:
            _dict['mappedDomain'] = None

        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if payment_id (nullable) is None
        # and model_fields_set contains the field
        if self.payment_id is None and "payment_id" in self.model_fields_set:
            _dict['paymentId'] = None

        # set to None if time_zone (nullable) is None
        # and model_fields_set contains the field
        if self.time_zone is None and "time_zone" in self.model_fields_set:
            _dict['timeZone'] = None

        # set to None if trusted_domains (nullable) is None
        # and model_fields_set contains the field
        if self.trusted_domains is None and "trusted_domains" in self.model_fields_set:
            _dict['trustedDomains'] = None

        # set to None if trusted_domains_raw (nullable) is None
        # and model_fields_set contains the field
        if self.trusted_domains_raw is None and "trusted_domains_raw" in self.model_fields_set:
            _dict['trustedDomainsRaw'] = None

        # set to None if region (nullable) is None
        # and model_fields_set contains the field
        if self.region is None and "region" in self.model_fields_set:
            _dict['region'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of TenantDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "affiliateId": obj.get("affiliateId"),
            "tenantAlias": obj.get("tenantAlias"),
            "calls": obj.get("calls"),
            "campaign": obj.get("campaign"),
            "creationDateTime": obj.get("creationDateTime"),
            "hostedRegion": obj.get("hostedRegion"),
            "tenantId": obj.get("tenantId"),
            "industry": obj.get("industry"),
            "language": obj.get("language"),
            "lastModified": obj.get("lastModified"),
            "mappedDomain": obj.get("mappedDomain"),
            "name": obj.get("name"),
            "ownerId": obj.get("ownerId"),
            "paymentId": obj.get("paymentId"),
            "spam": obj.get("spam"),
            "status": obj.get("status"),
            "statusChangeDate": obj.get("statusChangeDate"),
            "timeZone": obj.get("timeZone"),
            "trustedDomains": obj.get("trustedDomains"),
            "trustedDomainsRaw": obj.get("trustedDomainsRaw"),
            "trustedDomainsType": obj.get("trustedDomainsType"),
            "version": obj.get("version"),
            "versionChanged": obj.get("versionChanged"),
            "region": obj.get("region")
        })
        return _obj


