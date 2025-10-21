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
from typing import Optional, Set
from typing_extensions import Self

class PasswordSettingsDto(BaseModel):
    """
    The password settings parameters.
    """ # noqa: E501
    min_length: StrictInt = Field(description="The minimum number of characters required for valid passwords.", alias="minLength")
    upper_case: StrictBool = Field(description="Specifies whether the password should contain the uppercase letters or not.", alias="upperCase")
    digits: StrictBool = Field(description="Specifies whether the password should contain the digits or not.")
    spec_symbols: StrictBool = Field(description="Specifies whether the password should contain the special symbols or not.", alias="specSymbols")
    allowed_characters_regex_str: Optional[StrictStr] = Field(description="The allowed password characters in the regex string format.", alias="allowedCharactersRegexStr")
    digits_regex_str: Optional[StrictStr] = Field(description="The password digits in the regex string format.", alias="digitsRegexStr")
    upper_case_regex_str: Optional[StrictStr] = Field(description="The password uppercase letters in the regex string format.", alias="upperCaseRegexStr")
    spec_symbols_regex_str: Optional[StrictStr] = Field(description="The passaword special symbols in the regex string format.", alias="specSymbolsRegexStr")
    __properties: ClassVar[List[str]] = ["minLength", "upperCase", "digits", "specSymbols", "allowedCharactersRegexStr", "digitsRegexStr", "upperCaseRegexStr", "specSymbolsRegexStr"]

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
        """Create an instance of PasswordSettingsDto from a JSON string"""
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
        # set to None if allowed_characters_regex_str (nullable) is None
        # and model_fields_set contains the field
        if self.allowed_characters_regex_str is None and "allowed_characters_regex_str" in self.model_fields_set:
            _dict['allowedCharactersRegexStr'] = None

        # set to None if digits_regex_str (nullable) is None
        # and model_fields_set contains the field
        if self.digits_regex_str is None and "digits_regex_str" in self.model_fields_set:
            _dict['digitsRegexStr'] = None

        # set to None if upper_case_regex_str (nullable) is None
        # and model_fields_set contains the field
        if self.upper_case_regex_str is None and "upper_case_regex_str" in self.model_fields_set:
            _dict['upperCaseRegexStr'] = None

        # set to None if spec_symbols_regex_str (nullable) is None
        # and model_fields_set contains the field
        if self.spec_symbols_regex_str is None and "spec_symbols_regex_str" in self.model_fields_set:
            _dict['specSymbolsRegexStr'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PasswordSettingsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "minLength": obj.get("minLength"),
            "upperCase": obj.get("upperCase"),
            "digits": obj.get("digits"),
            "specSymbols": obj.get("specSymbols"),
            "allowedCharactersRegexStr": obj.get("allowedCharactersRegexStr"),
            "digitsRegexStr": obj.get("digitsRegexStr"),
            "upperCaseRegexStr": obj.get("upperCaseRegexStr"),
            "specSymbolsRegexStr": obj.get("specSymbolsRegexStr")
        })
        return _obj


