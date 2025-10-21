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


class TenantStatus(int, Enum):
    """
    [0 - Active, 1 - Suspended, 2 - Remove pending, 3 - Transfering, 4 - Restoring, 5 - Migrating, 6 - Encryption]
    """

    """
    allowed enum values
    """
    Active = 0
    Suspended = 1
    RemovePending = 2
    Transfering = 3
    Restoring = 4
    Migrating = 5
    Encryption = 6

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TenantStatus from a JSON string"""
        return cls(json.loads(json_str))


