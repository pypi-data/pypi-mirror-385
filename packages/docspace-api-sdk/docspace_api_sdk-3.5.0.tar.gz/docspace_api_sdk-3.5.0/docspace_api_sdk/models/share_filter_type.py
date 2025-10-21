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


class ShareFilterType(int, Enum):
    """
    [0 - User or group, 1 - Invitation link, 2 - External link, 4 - Additional external link, 8 - Primary external link, 16 - User, 32 - Group]
    """

    """
    allowed enum values
    """
    UserOrGroup = 0
    InvitationLink = 1
    ExternalLink = 2
    AdditionalExternalLink = 4
    PrimaryExternalLink = 8
    User = 16
    Group = 32

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ShareFilterType from a JSON string"""
        return cls(json.loads(json_str))


