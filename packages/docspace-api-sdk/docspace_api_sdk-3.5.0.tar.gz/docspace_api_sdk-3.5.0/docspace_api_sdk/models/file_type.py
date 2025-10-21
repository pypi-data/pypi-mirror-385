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


class FileType(int, Enum):
    """
    [0 - Unknown, 1 - Archive, 2 - Video, 3 - Audio, 4 - Image, 5 - Spreadsheet, 6 - Presentation, 7 - Document, 10 - Pdf, 11 - Diagram]
    """

    """
    allowed enum values
    """
    Unknown = 0
    Archive = 1
    Video = 2
    Audio = 3
    Image = 4
    Spreadsheet = 5
    Presentation = 6
    Document = 7
    Pdf = 10
    Diagram = 11

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of FileType from a JSON string"""
        return cls(json.loads(json_str))


