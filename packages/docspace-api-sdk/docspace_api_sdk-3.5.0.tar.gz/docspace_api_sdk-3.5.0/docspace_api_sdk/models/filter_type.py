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


class FilterType(int, Enum):
    """
    [0 - None, 1 - Files  only, 2 - Folders only, 3 - Documents only, 4 - Presentations only, 5 - Spreadsheets only, 7 - Images only, 8 - By user, 9 - By department, 10 - Archive only, 11 - By extension, 12 - Media only, 13 - Filling forms rooms, 14 - Editing rooms, 17 - Custom rooms, 20 - Public rooms, 22 - Pdf, 23 - Pdf form, 24 - Virtual data rooms, 25 - Diagrams only]
    """

    """
    allowed enum values
    """
    None = 0
    FilesOnly = 1
    FoldersOnly = 2
    DocumentsOnly = 3
    PresentationsOnly = 4
    SpreadsheetsOnly = 5
    ImagesOnly = 7
    ByUser = 8
    ByDepartment = 9
    ArchiveOnly = 10
    ByExtension = 11
    MediaOnly = 12
    FillingFormsRooms = 13
    EditingRooms = 14
    CustomRooms = 17
    PublicRooms = 20
    Pdf = 22
    PdfForm = 23
    VirtualDataRooms = 24
    DiagramsOnly = 25

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of FilterType from a JSON string"""
        return cls(json.loads(json_str))


