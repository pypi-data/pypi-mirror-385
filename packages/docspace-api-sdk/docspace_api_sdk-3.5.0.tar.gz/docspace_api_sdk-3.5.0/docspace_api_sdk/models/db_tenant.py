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
from typing_extensions import Annotated
from docspace_api_sdk.models.db_tenant_partner import DbTenantPartner
from docspace_api_sdk.models.tenant_industry import TenantIndustry
from docspace_api_sdk.models.tenant_status import TenantStatus
from docspace_api_sdk.models.tenant_trusted_domains_type import TenantTrustedDomainsType
from typing import Optional, Set
from typing_extensions import Self

class DbTenant(BaseModel):
    """
    The database tenant parameters.
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The tenant ID.")
    name: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The tenant name.")
    alias: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The tenant alias.")
    mapped_domain: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="Mapped domain", alias="mappedDomain")
    version: Optional[StrictInt] = Field(default=None, description="The tenant version.")
    version_changed: Optional[datetime] = Field(default=None, description="The Version_changed field.", alias="version_Changed")
    version_changed: Optional[datetime] = Field(default=None, description="The date and time when the version was changed.", alias="versionChanged")
    language: Optional[Annotated[str, Field(strict=True, max_length=10)]] = Field(default=None, description="The tenant language.")
    time_zone: Optional[Annotated[str, Field(strict=True, max_length=50)]] = Field(default=None, description="The tenant time zone.", alias="timeZone")
    trusted_domains_raw: Optional[Annotated[str, Field(strict=True, max_length=1024)]] = Field(default=None, description="The tenant trusted domains raw.", alias="trustedDomainsRaw")
    trusted_domains_enabled: Optional[TenantTrustedDomainsType] = Field(default=None, alias="trustedDomainsEnabled")
    status: Optional[TenantStatus] = None
    status_changed: Optional[datetime] = Field(default=None, description="The date and time when the tenant status was changed.", alias="statusChanged")
    status_changed_hack: Optional[datetime] = Field(default=None, description="The hacked date and time when the tenant status was changed.", alias="statusChangedHack")
    creation_date_time: Optional[datetime] = Field(default=None, description="The tenant creation date.", alias="creationDateTime")
    owner_id: Optional[StrictStr] = Field(default=None, description="The tenant owner ID.", alias="ownerId")
    payment_id: Optional[Annotated[str, Field(strict=True, max_length=38)]] = Field(default=None, description="The tenant payment ID.", alias="paymentId")
    industry: Optional[TenantIndustry] = None
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the tenant was last modified.", alias="lastModified")
    calls: Optional[StrictBool] = Field(default=None, description="Specifies if the calls are available for the current tenant or not.")
    partner: Optional[DbTenantPartner] = None
    __properties: ClassVar[List[str]] = ["id", "name", "alias", "mappedDomain", "version", "version_Changed", "versionChanged", "language", "timeZone", "trustedDomainsRaw", "trustedDomainsEnabled", "status", "statusChanged", "statusChangedHack", "creationDateTime", "ownerId", "paymentId", "industry", "lastModified", "calls", "partner"]

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
        """Create an instance of DbTenant from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of partner
        if self.partner:
            _dict['partner'] = self.partner.to_dict()
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if alias (nullable) is None
        # and model_fields_set contains the field
        if self.alias is None and "alias" in self.model_fields_set:
            _dict['alias'] = None

        # set to None if mapped_domain (nullable) is None
        # and model_fields_set contains the field
        if self.mapped_domain is None and "mapped_domain" in self.model_fields_set:
            _dict['mappedDomain'] = None

        # set to None if version_changed (nullable) is None
        # and model_fields_set contains the field
        if self.version_changed is None and "version_changed" in self.model_fields_set:
            _dict['version_Changed'] = None

        # set to None if language (nullable) is None
        # and model_fields_set contains the field
        if self.language is None and "language" in self.model_fields_set:
            _dict['language'] = None

        # set to None if time_zone (nullable) is None
        # and model_fields_set contains the field
        if self.time_zone is None and "time_zone" in self.model_fields_set:
            _dict['timeZone'] = None

        # set to None if trusted_domains_raw (nullable) is None
        # and model_fields_set contains the field
        if self.trusted_domains_raw is None and "trusted_domains_raw" in self.model_fields_set:
            _dict['trustedDomainsRaw'] = None

        # set to None if status_changed (nullable) is None
        # and model_fields_set contains the field
        if self.status_changed is None and "status_changed" in self.model_fields_set:
            _dict['statusChanged'] = None

        # set to None if owner_id (nullable) is None
        # and model_fields_set contains the field
        if self.owner_id is None and "owner_id" in self.model_fields_set:
            _dict['ownerId'] = None

        # set to None if payment_id (nullable) is None
        # and model_fields_set contains the field
        if self.payment_id is None and "payment_id" in self.model_fields_set:
            _dict['paymentId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DbTenant from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "name": obj.get("name"),
            "alias": obj.get("alias"),
            "mappedDomain": obj.get("mappedDomain"),
            "version": obj.get("version"),
            "version_Changed": obj.get("version_Changed"),
            "versionChanged": obj.get("versionChanged"),
            "language": obj.get("language"),
            "timeZone": obj.get("timeZone"),
            "trustedDomainsRaw": obj.get("trustedDomainsRaw"),
            "trustedDomainsEnabled": obj.get("trustedDomainsEnabled"),
            "status": obj.get("status"),
            "statusChanged": obj.get("statusChanged"),
            "statusChangedHack": obj.get("statusChangedHack"),
            "creationDateTime": obj.get("creationDateTime"),
            "ownerId": obj.get("ownerId"),
            "paymentId": obj.get("paymentId"),
            "industry": obj.get("industry"),
            "lastModified": obj.get("lastModified"),
            "calls": obj.get("calls"),
            "partner": DbTenantPartner.from_dict(obj["partner"]) if obj.get("partner") is not None else None
        })
        return _obj


