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
import json
from enum import Enum
from typing_extensions import Self


class BackupStorageType(int, Enum):
    """
    [0 - Documents, 1 - Thridparty documents, 2 - Custom cloud, 3 - Local, 4 - Data store, 5 - Thirdparty consumer]
    """

    """
    allowed enum values
    """
    Documents = 0
    ThridpartyDocuments = 1
    CustomCloud = 2
    Local = 3
    DataStore = 4
    ThirdPartyConsumer = 5

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of BackupStorageType from a JSON string"""
        return cls(json.loads(json_str))


