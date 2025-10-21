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
from typing import Optional, Set
from typing_extensions import Self

class PermissionsConfig(BaseModel):
    """
    The permissions configuration parameters.
    """ # noqa: E501
    comment: Optional[StrictBool] = Field(default=None, description="Defines if the document can be commented or not.")
    chat: Optional[StrictBool] = Field(default=None, description="Defines if the chat functionality is enabled in the document or not.")
    download: Optional[StrictBool] = Field(default=None, description="Defines if the document can be downloaded or only viewed or edited online.")
    edit: Optional[StrictBool] = Field(default=None, description="Defines if the document can be edited or only viewed.")
    fill_forms: Optional[StrictBool] = Field(default=None, description="Defines if the forms can be filled.", alias="fillForms")
    modify_filter: Optional[StrictBool] = Field(default=None, description="Defines if the filter can be applied globally (true) affecting all the other users,  or locally (false), i.e. for the current user only.", alias="modifyFilter")
    protect: Optional[StrictBool] = Field(default=None, description="Defines if the Protection tab on the toolbar and the Protect button in the left menu are displayedor hidden.")
    var_print: Optional[StrictBool] = Field(default=None, description="Defines if the document can be printed or not.", alias="print")
    review: Optional[StrictBool] = Field(default=None, description="Defines if the document can be reviewed or not.")
    copy: Optional[StrictBool] = Field(default=None, description="Defines if the content can be copied to the clipboard or not.")
    __properties: ClassVar[List[str]] = ["comment", "chat", "download", "edit", "fillForms", "modifyFilter", "protect", "print", "review", "copy"]

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
        """Create an instance of PermissionsConfig from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PermissionsConfig from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "comment": obj.get("comment"),
            "chat": obj.get("chat"),
            "download": obj.get("download"),
            "edit": obj.get("edit"),
            "fillForms": obj.get("fillForms"),
            "modifyFilter": obj.get("modifyFilter"),
            "protect": obj.get("protect"),
            "print": obj.get("print"),
            "review": obj.get("review"),
            "copy": obj.get("copy")
        })
        return _obj


