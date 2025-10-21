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


class FileShare(int, Enum):
    """
    [0 - None, 1 - Read and write, 2 - Read, 3 - Restrict, 4 - Varies, 5 - Review, 6 - Comment, 7 - Fill forms, 8 - Custom filter, 9 - Room manager, 10 - Editing, 11 - Content creator]
    """

    """
    allowed enum values
    """
    None = 0
    ReadWrite = 1
    Read = 2
    Restrict = 3
    Varies = 4
    Review = 5
    Comment = 6
    FillForms = 7
    CustomFilter = 8
    RoomManager = 9
    Editing = 10
    ContentCreator = 11

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of FileShare from a JSON string"""
        return cls(json.loads(json_str))


