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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.culture_specific_external_resource import CultureSpecificExternalResource
from typing import Optional, Set
from typing_extensions import Self

class CultureSpecificExternalResources(BaseModel):
    """
    The external resources settings.
    """ # noqa: E501
    api: Optional[CultureSpecificExternalResource] = None
    common: Optional[CultureSpecificExternalResource] = None
    forum: Optional[CultureSpecificExternalResource] = None
    helpcenter: Optional[CultureSpecificExternalResource] = None
    integrations: Optional[CultureSpecificExternalResource] = None
    site: Optional[CultureSpecificExternalResource] = None
    social_networks: Optional[CultureSpecificExternalResource] = Field(default=None, alias="socialNetworks")
    support: Optional[CultureSpecificExternalResource] = None
    videoguides: Optional[CultureSpecificExternalResource] = None
    __properties: ClassVar[List[str]] = ["api", "common", "forum", "helpcenter", "integrations", "site", "socialNetworks", "support", "videoguides"]

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
        """Create an instance of CultureSpecificExternalResources from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of api
        if self.api:
            _dict['api'] = self.api.to_dict()
        # override the default output from pydantic by calling `to_dict()` of common
        if self.common:
            _dict['common'] = self.common.to_dict()
        # override the default output from pydantic by calling `to_dict()` of forum
        if self.forum:
            _dict['forum'] = self.forum.to_dict()
        # override the default output from pydantic by calling `to_dict()` of helpcenter
        if self.helpcenter:
            _dict['helpcenter'] = self.helpcenter.to_dict()
        # override the default output from pydantic by calling `to_dict()` of integrations
        if self.integrations:
            _dict['integrations'] = self.integrations.to_dict()
        # override the default output from pydantic by calling `to_dict()` of site
        if self.site:
            _dict['site'] = self.site.to_dict()
        # override the default output from pydantic by calling `to_dict()` of social_networks
        if self.social_networks:
            _dict['socialNetworks'] = self.social_networks.to_dict()
        # override the default output from pydantic by calling `to_dict()` of support
        if self.support:
            _dict['support'] = self.support.to_dict()
        # override the default output from pydantic by calling `to_dict()` of videoguides
        if self.videoguides:
            _dict['videoguides'] = self.videoguides.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CultureSpecificExternalResources from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "api": CultureSpecificExternalResource.from_dict(obj["api"]) if obj.get("api") is not None else None,
            "common": CultureSpecificExternalResource.from_dict(obj["common"]) if obj.get("common") is not None else None,
            "forum": CultureSpecificExternalResource.from_dict(obj["forum"]) if obj.get("forum") is not None else None,
            "helpcenter": CultureSpecificExternalResource.from_dict(obj["helpcenter"]) if obj.get("helpcenter") is not None else None,
            "integrations": CultureSpecificExternalResource.from_dict(obj["integrations"]) if obj.get("integrations") is not None else None,
            "site": CultureSpecificExternalResource.from_dict(obj["site"]) if obj.get("site") is not None else None,
            "socialNetworks": CultureSpecificExternalResource.from_dict(obj["socialNetworks"]) if obj.get("socialNetworks") is not None else None,
            "support": CultureSpecificExternalResource.from_dict(obj["support"]) if obj.get("support") is not None else None,
            "videoguides": CultureSpecificExternalResource.from_dict(obj["videoguides"]) if obj.get("videoguides") is not None else None
        })
        return _obj


