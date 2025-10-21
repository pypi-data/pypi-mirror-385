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

class EncryptionKeysConfig(BaseModel):
    """
    The encryption keys of the editor configuration.
    """ # noqa: E501
    crypto_engine_id: Optional[StrictStr] = Field(default=None, description="The crypto engine ID of the encryption key.", alias="cryptoEngineId")
    private_key_enc: Optional[StrictStr] = Field(default=None, description="The private key.", alias="privateKeyEnc")
    public_key: Optional[StrictStr] = Field(default=None, description="The public key.", alias="publicKey")
    __properties: ClassVar[List[str]] = ["cryptoEngineId", "privateKeyEnc", "publicKey"]

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
        """Create an instance of EncryptionKeysConfig from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "crypto_engine_id",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # set to None if crypto_engine_id (nullable) is None
        # and model_fields_set contains the field
        if self.crypto_engine_id is None and "crypto_engine_id" in self.model_fields_set:
            _dict['cryptoEngineId'] = None

        # set to None if private_key_enc (nullable) is None
        # and model_fields_set contains the field
        if self.private_key_enc is None and "private_key_enc" in self.model_fields_set:
            _dict['privateKeyEnc'] = None

        # set to None if public_key (nullable) is None
        # and model_fields_set contains the field
        if self.public_key is None and "public_key" in self.model_fields_set:
            _dict['publicKey'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of EncryptionKeysConfig from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "cryptoEngineId": obj.get("cryptoEngineId"),
            "privateKeyEnc": obj.get("privateKeyEnc"),
            "publicKey": obj.get("publicKey")
        })
        return _obj


