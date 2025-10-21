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

class SsoSpCertificateAdvanced(BaseModel):
    """
    The SP advanced certificate parameters.
    """ # noqa: E501
    signing_algorithm: Optional[StrictStr] = Field(default=None, description="The certificate signing algorithm.", alias="signingAlgorithm")
    sign_auth_requests: Optional[StrictBool] = Field(default=None, description="Specifies if SP will sign the SAML authentication requests sent to IdP or not.", alias="signAuthRequests")
    sign_logout_requests: Optional[StrictBool] = Field(default=None, description="Specifies if SP will sign the SAML logout requests sent to IdP or not.", alias="signLogoutRequests")
    sign_logout_responses: Optional[StrictBool] = Field(default=None, description="Specifies if SP will sign the SAML logout responses sent to IdP or not.", alias="signLogoutResponses")
    encrypt_algorithm: Optional[StrictStr] = Field(default=None, description="The certificate encryption algorithm.", alias="encryptAlgorithm")
    decrypt_algorithm: Optional[StrictStr] = Field(default=None, description="The certificate decryption algorithm.", alias="decryptAlgorithm")
    encrypt_assertions: Optional[StrictBool] = Field(default=None, description="Specifies if the assertions will be encrypted or not.", alias="encryptAssertions")
    __properties: ClassVar[List[str]] = ["signingAlgorithm", "signAuthRequests", "signLogoutRequests", "signLogoutResponses", "encryptAlgorithm", "decryptAlgorithm", "encryptAssertions"]

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
        """Create an instance of SsoSpCertificateAdvanced from a JSON string"""
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
        # set to None if signing_algorithm (nullable) is None
        # and model_fields_set contains the field
        if self.signing_algorithm is None and "signing_algorithm" in self.model_fields_set:
            _dict['signingAlgorithm'] = None

        # set to None if encrypt_algorithm (nullable) is None
        # and model_fields_set contains the field
        if self.encrypt_algorithm is None and "encrypt_algorithm" in self.model_fields_set:
            _dict['encryptAlgorithm'] = None

        # set to None if decrypt_algorithm (nullable) is None
        # and model_fields_set contains the field
        if self.decrypt_algorithm is None and "decrypt_algorithm" in self.model_fields_set:
            _dict['decryptAlgorithm'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SsoSpCertificateAdvanced from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "signingAlgorithm": obj.get("signingAlgorithm"),
            "signAuthRequests": obj.get("signAuthRequests"),
            "signLogoutRequests": obj.get("signLogoutRequests"),
            "signLogoutResponses": obj.get("signLogoutResponses"),
            "encryptAlgorithm": obj.get("encryptAlgorithm"),
            "decryptAlgorithm": obj.get("decryptAlgorithm"),
            "encryptAssertions": obj.get("encryptAssertions")
        })
        return _obj


