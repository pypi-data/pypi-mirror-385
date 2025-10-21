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


class ActionType(int, Enum):
    """
    [0 - None, 1 - Create, 2 - Update, 3 - Delete, 4 - Link, 5 - Unlink, 6 - Attach, 7 - Detach, 8 - Send, 9 - Import, 10 - Export, 11 - Update access, 12 - Download, 13 - Upload, 14 - Copy, 15 - Move, 16 - Reassigns, 17 - Follow, 18 - Unfollow, 19 - Logout]
    """

    """
    allowed enum values
    """
    None = 0
    Create = 1
    Update = 2
    Delete = 3
    Link = 4
    Unlink = 5
    Attach = 6
    Detach = 7
    Send = 8
    Import = 9
    Export = 10
    UpdateAccess = 11
    Download = 12
    Upload = 13
    Copy = 14
    Move = 15
    Reassigns = 16
    Follow = 17
    Unfollow = 18
    Logout = 19

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ActionType from a JSON string"""
        return cls(json.loads(json_str))


