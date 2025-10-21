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


class FolderType(int, Enum):
    """
    [0 - Default, 1 - Coomon, 2 - Bunch, 3 - Trash, 5 - User, 6 - Share, 8 - Projects, 10 - Favourites, 11 - Recent, 12 - Templates, 13 - Privacy, 14 - Virtual rooms, 15 - Filling forms room, 16 - Editing room, 19 - Custom room, 20 - Archive, 21 - Thirdparty backup, 22 - Public room, 25 - Ready form folder, 26 - In process form folder, 27 - Form filling folder done, 28 - Form filling folder in progress, 29 - Virtual Data Room, 30 - Room templates folder]
    """

    """
    allowed enum values
    """
    DEFAULT = 0
    COMMON = 1
    BUNCH = 2
    TRASH = 3
    USER = 5
    SHARE = 6
    Projects = 8
    Favorites = 10
    Recent = 11
    Templates = 12
    Privacy = 13
    VirtualRooms = 14
    FillingFormsRoom = 15
    EditingRoom = 16
    CustomRoom = 19
    Archive = 20
    ThirdpartyBackup = 21
    PublicRoom = 22
    ReadyFormFolder = 25
    InProcessFormFolder = 26
    FormFillingFolderDone = 27
    FormFillingFolderInProgress = 28
    VirtualDataRoom = 29
    RoomTemplates = 30

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of FolderType from a JSON string"""
        return cls(json.loads(json_str))


