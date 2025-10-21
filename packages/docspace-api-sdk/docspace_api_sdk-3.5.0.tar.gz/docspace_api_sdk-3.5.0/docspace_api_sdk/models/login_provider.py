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


class LoginProvider(int, Enum):
    """
    [0 - Facebook, 1 - Google, 2 - Dropbox, 3 - Docusign, 4 - Box, 5 - OneDrive, 6 - GosUslugi, 7 - LinkedIn, 8 - MailRu, 9 - VK, 10 - Wordpress, 11 - Yahoo, 12 - Yandex]
    """

    """
    allowed enum values
    """
    Facebook = 0
    Google = 1
    Dropbox = 2
    Docusign = 3
    Box = 4
    OneDrive = 5
    GosUslugi = 6
    LinkedIn = 7
    MailRu = 8
    VK = 9
    Wordpress = 10
    Yahoo = 11
    Yandex = 12

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of LoginProvider from a JSON string"""
        return cls(json.loads(json_str))


