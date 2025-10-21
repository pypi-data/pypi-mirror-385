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
from docspace_api_sdk.models.sso_certificate import SsoCertificate
from docspace_api_sdk.models.sso_field_mapping import SsoFieldMapping
from docspace_api_sdk.models.sso_idp_certificate_advanced import SsoIdpCertificateAdvanced
from docspace_api_sdk.models.sso_idp_settings import SsoIdpSettings
from docspace_api_sdk.models.sso_sp_certificate_advanced import SsoSpCertificateAdvanced
from typing import Optional, Set
from typing_extensions import Self

class SsoSettingsV2(BaseModel):
    """
    The SSO portal settings.
    """ # noqa: E501
    last_modified: Optional[datetime] = Field(default=None, alias="lastModified")
    enable_sso: Optional[StrictBool] = Field(default=None, description="Specifies if the SSO settings are enabled or not.", alias="enableSso")
    idp_settings: Optional[SsoIdpSettings] = Field(default=None, alias="idpSettings")
    idp_certificates: Optional[List[SsoCertificate]] = Field(default=None, description="The list of the IdP certificates.", alias="idpCertificates")
    idp_certificate_advanced: Optional[SsoIdpCertificateAdvanced] = Field(default=None, alias="idpCertificateAdvanced")
    sp_login_label: Optional[StrictStr] = Field(default=None, description="The SP login label.", alias="spLoginLabel")
    sp_certificates: Optional[List[SsoCertificate]] = Field(default=None, description="The list of the SP certificates.", alias="spCertificates")
    sp_certificate_advanced: Optional[SsoSpCertificateAdvanced] = Field(default=None, alias="spCertificateAdvanced")
    field_mapping: Optional[SsoFieldMapping] = Field(default=None, alias="fieldMapping")
    hide_auth_page: Optional[StrictBool] = Field(default=None, description="Specifies if the authentication page will be hidden or not.", alias="hideAuthPage")
    users_type: Optional[StrictInt] = Field(default=None, description="The user type.", alias="usersType")
    disable_email_verification: Optional[StrictBool] = Field(default=None, description="Specifies if the email verification is disabled or not.", alias="disableEmailVerification")
    __properties: ClassVar[List[str]] = ["lastModified", "enableSso", "idpSettings", "idpCertificates", "idpCertificateAdvanced", "spLoginLabel", "spCertificates", "spCertificateAdvanced", "fieldMapping", "hideAuthPage", "usersType", "disableEmailVerification"]

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
        """Create an instance of SsoSettingsV2 from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of idp_settings
        if self.idp_settings:
            _dict['idpSettings'] = self.idp_settings.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in idp_certificates (list)
        _items = []
        if self.idp_certificates:
            for _item_idp_certificates in self.idp_certificates:
                if _item_idp_certificates:
                    _items.append(_item_idp_certificates.to_dict())
            _dict['idpCertificates'] = _items
        # override the default output from pydantic by calling `to_dict()` of idp_certificate_advanced
        if self.idp_certificate_advanced:
            _dict['idpCertificateAdvanced'] = self.idp_certificate_advanced.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in sp_certificates (list)
        _items = []
        if self.sp_certificates:
            for _item_sp_certificates in self.sp_certificates:
                if _item_sp_certificates:
                    _items.append(_item_sp_certificates.to_dict())
            _dict['spCertificates'] = _items
        # override the default output from pydantic by calling `to_dict()` of sp_certificate_advanced
        if self.sp_certificate_advanced:
            _dict['spCertificateAdvanced'] = self.sp_certificate_advanced.to_dict()
        # override the default output from pydantic by calling `to_dict()` of field_mapping
        if self.field_mapping:
            _dict['fieldMapping'] = self.field_mapping.to_dict()
        # set to None if enable_sso (nullable) is None
        # and model_fields_set contains the field
        if self.enable_sso is None and "enable_sso" in self.model_fields_set:
            _dict['enableSso'] = None

        # set to None if idp_certificates (nullable) is None
        # and model_fields_set contains the field
        if self.idp_certificates is None and "idp_certificates" in self.model_fields_set:
            _dict['idpCertificates'] = None

        # set to None if sp_login_label (nullable) is None
        # and model_fields_set contains the field
        if self.sp_login_label is None and "sp_login_label" in self.model_fields_set:
            _dict['spLoginLabel'] = None

        # set to None if sp_certificates (nullable) is None
        # and model_fields_set contains the field
        if self.sp_certificates is None and "sp_certificates" in self.model_fields_set:
            _dict['spCertificates'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SsoSettingsV2 from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "lastModified": obj.get("lastModified"),
            "enableSso": obj.get("enableSso"),
            "idpSettings": SsoIdpSettings.from_dict(obj["idpSettings"]) if obj.get("idpSettings") is not None else None,
            "idpCertificates": [SsoCertificate.from_dict(_item) for _item in obj["idpCertificates"]] if obj.get("idpCertificates") is not None else None,
            "idpCertificateAdvanced": SsoIdpCertificateAdvanced.from_dict(obj["idpCertificateAdvanced"]) if obj.get("idpCertificateAdvanced") is not None else None,
            "spLoginLabel": obj.get("spLoginLabel"),
            "spCertificates": [SsoCertificate.from_dict(_item) for _item in obj["spCertificates"]] if obj.get("spCertificates") is not None else None,
            "spCertificateAdvanced": SsoSpCertificateAdvanced.from_dict(obj["spCertificateAdvanced"]) if obj.get("spCertificateAdvanced") is not None else None,
            "fieldMapping": SsoFieldMapping.from_dict(obj["fieldMapping"]) if obj.get("fieldMapping") is not None else None,
            "hideAuthPage": obj.get("hideAuthPage"),
            "usersType": obj.get("usersType"),
            "disableEmailVerification": obj.get("disableEmailVerification")
        })
        return _obj


