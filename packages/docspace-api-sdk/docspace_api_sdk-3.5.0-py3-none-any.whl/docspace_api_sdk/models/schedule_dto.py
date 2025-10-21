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
from docspace_api_sdk.models.backup_storage_type import BackupStorageType
from docspace_api_sdk.models.cron_params import CronParams
from typing import Optional, Set
from typing_extensions import Self

class ScheduleDto(BaseModel):
    """
    ScheduleDto
    """ # noqa: E501
    storage_type: BackupStorageType = Field(alias="storageType")
    storage_params: Optional[Dict[str, Optional[StrictStr]]] = Field(alias="storageParams")
    cron_params: CronParams = Field(alias="cronParams")
    backups_stored: Optional[StrictInt] = Field(default=None, alias="backupsStored")
    last_backup_time: datetime = Field(alias="lastBackupTime")
    dump: StrictBool
    __properties: ClassVar[List[str]] = ["storageType", "storageParams", "cronParams", "backupsStored", "lastBackupTime", "dump"]

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
        """Create an instance of ScheduleDto from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of cron_params
        if self.cron_params:
            _dict['cronParams'] = self.cron_params.to_dict()
        # set to None if storage_params (nullable) is None
        # and model_fields_set contains the field
        if self.storage_params is None and "storage_params" in self.model_fields_set:
            _dict['storageParams'] = None

        # set to None if backups_stored (nullable) is None
        # and model_fields_set contains the field
        if self.backups_stored is None and "backups_stored" in self.model_fields_set:
            _dict['backupsStored'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ScheduleDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "storageType": obj.get("storageType"),
            "storageParams": obj.get("storageParams"),
            "cronParams": CronParams.from_dict(obj["cronParams"]) if obj.get("cronParams") is not None else None,
            "backupsStored": obj.get("backupsStored"),
            "lastBackupTime": obj.get("lastBackupTime"),
            "dump": obj.get("dump")
        })
        return _obj


