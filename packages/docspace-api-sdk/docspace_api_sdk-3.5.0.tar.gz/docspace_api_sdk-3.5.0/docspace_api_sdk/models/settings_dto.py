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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from docspace_api_sdk.models.culture_specific_external_resources import CultureSpecificExternalResources
from docspace_api_sdk.models.deep_link_dto import DeepLinkDto
from docspace_api_sdk.models.firebase_dto import FirebaseDto
from docspace_api_sdk.models.form_gallery_dto import FormGalleryDto
from docspace_api_sdk.models.password_hasher import PasswordHasher
from docspace_api_sdk.models.plugins_dto import PluginsDto
from docspace_api_sdk.models.recaptcha_type import RecaptchaType
from docspace_api_sdk.models.tenant_domain_validator import TenantDomainValidator
from docspace_api_sdk.models.tenant_status import TenantStatus
from docspace_api_sdk.models.tenant_trusted_domains_type import TenantTrustedDomainsType
from typing import Optional, Set
from typing_extensions import Self

class SettingsDto(BaseModel):
    """
    The settings information.
    """ # noqa: E501
    timezone: Optional[StrictStr] = Field(default=None, description="The time zone.")
    trusted_domains: Optional[List[StrictStr]] = Field(default=None, description="The list of the trusted domains.", alias="trustedDomains")
    trusted_domains_type: Optional[TenantTrustedDomainsType] = Field(default=None, alias="trustedDomainsType")
    culture: Optional[StrictStr] = Field(description="The language.")
    utc_offset: Optional[StrictStr] = Field(default=None, description="The UTC offset in the TimeSpan format.", alias="utcOffset")
    utc_hours_offset: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The UTC offset in hours.", alias="utcHoursOffset")
    greeting_settings: Optional[StrictStr] = Field(default=None, description="The greeting settings.", alias="greetingSettings")
    owner_id: Optional[StrictStr] = Field(default=None, description="The owner ID.", alias="ownerId")
    name_schema_id: Optional[StrictStr] = Field(default=None, description="The team template ID.", alias="nameSchemaId")
    enabled_join: Optional[StrictBool] = Field(default=None, description="Specifies if a user can join the portal or not.", alias="enabledJoin")
    enable_adm_mess: Optional[StrictBool] = Field(default=None, description="Specifies if a user can send a message to the administrator when accessing the DocSpace portal or not.", alias="enableAdmMess")
    thirdparty_enable: Optional[StrictBool] = Field(default=None, description="Specifies if a user can connect third-party providers to the portal or not.", alias="thirdpartyEnable")
    doc_space: Optional[StrictBool] = Field(default=None, description="Specifies if this portal is a DocSpace portal or not.", alias="docSpace")
    standalone: Optional[StrictBool] = Field(default=None, description="Indicates whether the system is running in standalone mode.")
    is_ami: Optional[StrictBool] = Field(default=None, description="Specifies if this portal is the AMI instance or not.", alias="isAmi")
    base_domain: Optional[StrictStr] = Field(description="The base domain.", alias="baseDomain")
    wizard_token: Optional[StrictStr] = Field(default=None, description="The wizard token.", alias="wizardToken")
    password_hash: Optional[PasswordHasher] = Field(default=None, alias="passwordHash")
    firebase: Optional[FirebaseDto] = None
    version: Optional[StrictStr] = Field(default=None, description="The portal version.")
    recaptcha_type: Optional[RecaptchaType] = Field(default=None, alias="recaptchaType")
    recaptcha_public_key: Optional[StrictStr] = Field(default=None, description="The ReCAPTCHA public key.", alias="recaptchaPublicKey")
    debug_info: Optional[StrictBool] = Field(default=None, description="Specifies if the debug information will be sent or not.", alias="debugInfo")
    socket_url: Optional[StrictStr] = Field(default=None, description="The socket URL.", alias="socketUrl")
    tenant_status: Optional[TenantStatus] = Field(default=None, alias="tenantStatus")
    tenant_alias: Optional[StrictStr] = Field(default=None, description="The tenant alias.", alias="tenantAlias")
    display_about: Optional[StrictBool] = Field(default=None, description="Specifies whether to display the About portal section.", alias="displayAbout")
    domain_validator: Optional[TenantDomainValidator] = Field(default=None, alias="domainValidator")
    zendesk_key: Optional[StrictStr] = Field(default=None, description="The Zendesk key.", alias="zendeskKey")
    tag_manager_id: Optional[StrictStr] = Field(default=None, description="The tag manager ID.", alias="tagManagerId")
    cookie_settings_enabled: StrictBool = Field(description="Specifies whether the cookie settings are enabled.", alias="cookieSettingsEnabled")
    limited_access_space: Optional[StrictBool] = Field(default=None, description="Specifies whether the access to the space management is limited or not.", alias="limitedAccessSpace")
    limited_access_dev_tools_for_users: Optional[StrictBool] = Field(default=None, description="Specifies whether the access to the Developer Tools is limited for users or not.", alias="limitedAccessDevToolsForUsers")
    display_banners: Optional[StrictBool] = Field(default=None, description="Specifies whether to display the promotional banners.", alias="displayBanners")
    user_name_regex: Optional[StrictStr] = Field(default=None, description="The user name validation regex.", alias="userNameRegex")
    invitation_limit: Optional[StrictInt] = Field(default=None, description="The maximum number of invitations to the portal.", alias="invitationLimit")
    plugins: Optional[PluginsDto] = None
    deep_link: DeepLinkDto = Field(alias="deepLink")
    form_gallery: Optional[FormGalleryDto] = Field(default=None, alias="formGallery")
    max_image_upload_size: Optional[StrictInt] = Field(default=None, description="The maximum image upload size.", alias="maxImageUploadSize")
    logo_text: Optional[StrictStr] = Field(default=None, description="The white label logo text.", alias="logoText")
    external_resources: Optional[CultureSpecificExternalResources] = Field(default=None, alias="externalResources")
    __properties: ClassVar[List[str]] = ["timezone", "trustedDomains", "trustedDomainsType", "culture", "utcOffset", "utcHoursOffset", "greetingSettings", "ownerId", "nameSchemaId", "enabledJoin", "enableAdmMess", "thirdpartyEnable", "docSpace", "standalone", "isAmi", "baseDomain", "wizardToken", "passwordHash", "firebase", "version", "recaptchaType", "recaptchaPublicKey", "debugInfo", "socketUrl", "tenantStatus", "tenantAlias", "displayAbout", "domainValidator", "zendeskKey", "tagManagerId", "cookieSettingsEnabled", "limitedAccessSpace", "limitedAccessDevToolsForUsers", "displayBanners", "userNameRegex", "invitationLimit", "plugins", "deepLink", "formGallery", "maxImageUploadSize", "logoText", "externalResources"]

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
        """Create an instance of SettingsDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of password_hash
        if self.password_hash:
            _dict['passwordHash'] = self.password_hash.to_dict()
        # override the default output from pydantic by calling `to_dict()` of firebase
        if self.firebase:
            _dict['firebase'] = self.firebase.to_dict()
        # override the default output from pydantic by calling `to_dict()` of domain_validator
        if self.domain_validator:
            _dict['domainValidator'] = self.domain_validator.to_dict()
        # override the default output from pydantic by calling `to_dict()` of plugins
        if self.plugins:
            _dict['plugins'] = self.plugins.to_dict()
        # override the default output from pydantic by calling `to_dict()` of deep_link
        if self.deep_link:
            _dict['deepLink'] = self.deep_link.to_dict()
        # override the default output from pydantic by calling `to_dict()` of form_gallery
        if self.form_gallery:
            _dict['formGallery'] = self.form_gallery.to_dict()
        # override the default output from pydantic by calling `to_dict()` of external_resources
        if self.external_resources:
            _dict['externalResources'] = self.external_resources.to_dict()
        # set to None if timezone (nullable) is None
        # and model_fields_set contains the field
        if self.timezone is None and "timezone" in self.model_fields_set:
            _dict['timezone'] = None

        # set to None if trusted_domains (nullable) is None
        # and model_fields_set contains the field
        if self.trusted_domains is None and "trusted_domains" in self.model_fields_set:
            _dict['trustedDomains'] = None

        # set to None if culture (nullable) is None
        # and model_fields_set contains the field
        if self.culture is None and "culture" in self.model_fields_set:
            _dict['culture'] = None

        # set to None if greeting_settings (nullable) is None
        # and model_fields_set contains the field
        if self.greeting_settings is None and "greeting_settings" in self.model_fields_set:
            _dict['greetingSettings'] = None

        # set to None if name_schema_id (nullable) is None
        # and model_fields_set contains the field
        if self.name_schema_id is None and "name_schema_id" in self.model_fields_set:
            _dict['nameSchemaId'] = None

        # set to None if enabled_join (nullable) is None
        # and model_fields_set contains the field
        if self.enabled_join is None and "enabled_join" in self.model_fields_set:
            _dict['enabledJoin'] = None

        # set to None if enable_adm_mess (nullable) is None
        # and model_fields_set contains the field
        if self.enable_adm_mess is None and "enable_adm_mess" in self.model_fields_set:
            _dict['enableAdmMess'] = None

        # set to None if thirdparty_enable (nullable) is None
        # and model_fields_set contains the field
        if self.thirdparty_enable is None and "thirdparty_enable" in self.model_fields_set:
            _dict['thirdpartyEnable'] = None

        # set to None if base_domain (nullable) is None
        # and model_fields_set contains the field
        if self.base_domain is None and "base_domain" in self.model_fields_set:
            _dict['baseDomain'] = None

        # set to None if wizard_token (nullable) is None
        # and model_fields_set contains the field
        if self.wizard_token is None and "wizard_token" in self.model_fields_set:
            _dict['wizardToken'] = None

        # set to None if version (nullable) is None
        # and model_fields_set contains the field
        if self.version is None and "version" in self.model_fields_set:
            _dict['version'] = None

        # set to None if recaptcha_public_key (nullable) is None
        # and model_fields_set contains the field
        if self.recaptcha_public_key is None and "recaptcha_public_key" in self.model_fields_set:
            _dict['recaptchaPublicKey'] = None

        # set to None if socket_url (nullable) is None
        # and model_fields_set contains the field
        if self.socket_url is None and "socket_url" in self.model_fields_set:
            _dict['socketUrl'] = None

        # set to None if tenant_alias (nullable) is None
        # and model_fields_set contains the field
        if self.tenant_alias is None and "tenant_alias" in self.model_fields_set:
            _dict['tenantAlias'] = None

        # set to None if zendesk_key (nullable) is None
        # and model_fields_set contains the field
        if self.zendesk_key is None and "zendesk_key" in self.model_fields_set:
            _dict['zendeskKey'] = None

        # set to None if tag_manager_id (nullable) is None
        # and model_fields_set contains the field
        if self.tag_manager_id is None and "tag_manager_id" in self.model_fields_set:
            _dict['tagManagerId'] = None

        # set to None if user_name_regex (nullable) is None
        # and model_fields_set contains the field
        if self.user_name_regex is None and "user_name_regex" in self.model_fields_set:
            _dict['userNameRegex'] = None

        # set to None if invitation_limit (nullable) is None
        # and model_fields_set contains the field
        if self.invitation_limit is None and "invitation_limit" in self.model_fields_set:
            _dict['invitationLimit'] = None

        # set to None if logo_text (nullable) is None
        # and model_fields_set contains the field
        if self.logo_text is None and "logo_text" in self.model_fields_set:
            _dict['logoText'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SettingsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "timezone": obj.get("timezone"),
            "trustedDomains": obj.get("trustedDomains"),
            "trustedDomainsType": obj.get("trustedDomainsType"),
            "culture": obj.get("culture"),
            "utcOffset": obj.get("utcOffset"),
            "utcHoursOffset": obj.get("utcHoursOffset"),
            "greetingSettings": obj.get("greetingSettings"),
            "ownerId": obj.get("ownerId"),
            "nameSchemaId": obj.get("nameSchemaId"),
            "enabledJoin": obj.get("enabledJoin"),
            "enableAdmMess": obj.get("enableAdmMess"),
            "thirdpartyEnable": obj.get("thirdpartyEnable"),
            "docSpace": obj.get("docSpace"),
            "standalone": obj.get("standalone"),
            "isAmi": obj.get("isAmi"),
            "baseDomain": obj.get("baseDomain"),
            "wizardToken": obj.get("wizardToken"),
            "passwordHash": PasswordHasher.from_dict(obj["passwordHash"]) if obj.get("passwordHash") is not None else None,
            "firebase": FirebaseDto.from_dict(obj["firebase"]) if obj.get("firebase") is not None else None,
            "version": obj.get("version"),
            "recaptchaType": obj.get("recaptchaType"),
            "recaptchaPublicKey": obj.get("recaptchaPublicKey"),
            "debugInfo": obj.get("debugInfo"),
            "socketUrl": obj.get("socketUrl"),
            "tenantStatus": obj.get("tenantStatus"),
            "tenantAlias": obj.get("tenantAlias"),
            "displayAbout": obj.get("displayAbout"),
            "domainValidator": TenantDomainValidator.from_dict(obj["domainValidator"]) if obj.get("domainValidator") is not None else None,
            "zendeskKey": obj.get("zendeskKey"),
            "tagManagerId": obj.get("tagManagerId"),
            "cookieSettingsEnabled": obj.get("cookieSettingsEnabled"),
            "limitedAccessSpace": obj.get("limitedAccessSpace"),
            "limitedAccessDevToolsForUsers": obj.get("limitedAccessDevToolsForUsers"),
            "displayBanners": obj.get("displayBanners"),
            "userNameRegex": obj.get("userNameRegex"),
            "invitationLimit": obj.get("invitationLimit"),
            "plugins": PluginsDto.from_dict(obj["plugins"]) if obj.get("plugins") is not None else None,
            "deepLink": DeepLinkDto.from_dict(obj["deepLink"]) if obj.get("deepLink") is not None else None,
            "formGallery": FormGalleryDto.from_dict(obj["formGallery"]) if obj.get("formGallery") is not None else None,
            "maxImageUploadSize": obj.get("maxImageUploadSize"),
            "logoText": obj.get("logoText"),
            "externalResources": CultureSpecificExternalResources.from_dict(obj["externalResources"]) if obj.get("externalResources") is not None else None
        })
        return _obj


