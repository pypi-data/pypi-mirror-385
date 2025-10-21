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


class DistributedTaskStatus(int, Enum):
    """
    [0 - Created, 1 - Running, 2 - Completed, 3 - Canceled, 4 - Failted]
    """

    """
    allowed enum values
    """
    Created = 0
    Running = 1
    Completed = 2
    Canceled = 3
    Failted = 4

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of DistributedTaskStatus from a JSON string"""
        return cls(json.loads(json_str))


