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


class ConfirmType(int, Enum):
    """
    [0 - Emp invite, 1 - Link invite, 2 - Portal suspend, 3 - Portal continue, 4 - Portal remove, 5 - Dns change, 6 - Portal owner change, 7 - Activation, 8 - Email change, 9 - Email activation, 10 - Password change, 11 - Profile remove, 12 - Phone activation, 13 - Phone auth, 14 - Auth, 15 - Tfa activation, 16 - Tfa auth, 17 - Wizard, 18 - Guest share link]
    """

    """
    allowed enum values
    """
    EmpInvite = 0
    LinkInvite = 1
    PortalSuspend = 2
    PortalContinue = 3
    PortalRemove = 4
    DnsChange = 5
    PortalOwnerChange = 6
    Activation = 7
    EmailChange = 8
    EmailActivation = 9
    PasswordChange = 10
    ProfileRemove = 11
    PhoneActivation = 12
    PhoneAuth = 13
    Auth = 14
    TfaActivation = 15
    TfaAuth = 16
    Wizard = 17
    GuestShareLink = 18

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ConfirmType from a JSON string"""
        return cls(json.loads(json_str))


