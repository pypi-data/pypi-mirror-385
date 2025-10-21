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


class SortedByType(int, Enum):
    """
    [0 - Date and time, 1 - AZ, 2 - Size, 3 - Author, 4 - Type, 5 - New, 6 - Date and time creation, 7 - Room type, 8 - Tags, 9 - Room, 10 - Custom order, 11 - Last opened, 12 - Used space]
    """

    """
    allowed enum values
    """
    DateAndTime = 0
    AZ = 1
    Size = 2
    Author = 3
    Type = 4
    New = 5
    DateAndTimeCreation = 6
    RoomType = 7
    Tags = 8
    Room = 9
    CustomOrder = 10
    LastOpened = 11
    UsedSpace = 12

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of SortedByType from a JSON string"""
        return cls(json.loads(json_str))


