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


class FormFillingStatus(int, Enum):
    """
    [0 - None, 1 - Draft, 2 - You turn, 3 - In progress, 4 - Complete, 5 - Stoped]
    """

    """
    allowed enum values
    """
    None = 0
    Draft = 1
    YouTurn = 2
    InProgress = 3
    Complete = 4
    Stoped = 5

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of FormFillingStatus from a JSON string"""
        return cls(json.loads(json_str))


