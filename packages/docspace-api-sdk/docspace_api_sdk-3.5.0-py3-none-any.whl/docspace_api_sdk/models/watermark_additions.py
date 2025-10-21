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


class WatermarkAdditions(int, Enum):
    """
    [1 - User name, 2 - User email, 4 - User ip adress, 8 - Current date, 16 - Room name]
    """

    """
    allowed enum values
    """
    UserName = 1
    UserEmail = 2
    UserIpAdress = 4
    CurrentDate = 8
    RoomName = 16

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of WatermarkAdditions from a JSON string"""
        return cls(json.loads(json_str))


