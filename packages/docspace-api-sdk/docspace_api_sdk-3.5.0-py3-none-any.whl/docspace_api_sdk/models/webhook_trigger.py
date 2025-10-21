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


class WebhookTrigger(int, Enum):
    """
    [0 - *, 1 - user.created, 2 - user.invited, 4 - user.updated, 8 - user.deleted, 16 - group.created, 32 - group.updated, 64 - group.deleted, 128 - file.created, 256 - file.uploaded, 512 - file.updated, 1024 - file.trashed, 2048 - file.deleted, 4096 - file.restored, 8192 - file.copied, 16384 - file.moved, 32768 - folder.created, 65536 - folder.updated, 131072 - folder.trashed, 262144 - folder.deleted, 524288 - folder.restored, 1048576 - folder.copied, 2097152 - folder.moved, 4194304 - room.created, 8388608 - room.updated, 16777216 - room.archived, 33554432 - room.deleted, 67108864 - room.restored, 134217728 - room.copied]
    """

    """
    allowed enum values
    """
    All = 0
    UserCreated = 1
    UserInvited = 2
    UserUpdated = 4
    UserDeleted = 8
    GroupCreated = 16
    GroupUpdated = 32
    GroupDeleted = 64
    FileCreated = 128
    FileUploaded = 256
    FileUpdated = 512
    FileTrashed = 1024
    FileDeleted = 2048
    FileRestored = 4096
    FileCopied = 8192
    FileMoved = 16384
    FolderCreated = 32768
    FolderUpdated = 65536
    FolderTrashed = 131072
    FolderDeleted = 262144
    FolderRestored = 524288
    FolderCopied = 1048576
    FolderMoved = 2097152
    RoomCreated = 4194304
    RoomUpdated = 8388608
    RoomArchived = 16777216
    RoomDeleted = 33554432
    RoomRestored = 67108864
    RoomCopied = 134217728

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of WebhookTrigger from a JSON string"""
        return cls(json.loads(json_str))


