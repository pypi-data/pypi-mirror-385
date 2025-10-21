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


class WebhookGroupStatus(int, Enum):
    """
    [0 - None, 1 - Not sent, 2 - Status2xx, 4 - Status3xx, 8 - Status4xx, 16 - Status5xx]
    """

    """
    allowed enum values
    """
    None = 0
    NotSent = 1
    Status2xx = 2
    Status3xx = 4
    Status4xx = 8
    Status5xx = 16

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of WebhookGroupStatus from a JSON string"""
        return cls(json.loads(json_str))


