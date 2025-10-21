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


class ProviderFilter(int, Enum):
    """
    [0 - None, 1 - Box, 2 - DropBox, 3 - GoogleDrive, 4 - kDrive, 5 - OneDrive, 6 - SharePoint, 7 - WebDav, 8 - Yandex, 9 - Storage]
    """

    """
    allowed enum values
    """
    None = 0
    Box = 1
    DropBox = 2
    GoogleDrive = 3
    kDrive = 4
    OneDrive = 5
    SharePoint = 6
    WebDav = 7
    Yandex = 8
    Storage = 9

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ProviderFilter from a JSON string"""
        return cls(json.loads(json_str))


