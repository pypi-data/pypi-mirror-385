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


class LocationType(int, Enum):
    """
    [0 - None, 1 - Files, 2 - Folders, 3 - Documents settings, 4 - Companies, 5 - Persons, 6 - Contacts, 7 - Crm tasks, 8 - Opportunities, 9 - Invoices, 10 - Cases, 11 - Common crm settings, 12 - Contacts settings, 13 - Contact types, 14 - Invoice settings, 15 - Other crm settings, 16 - Users, 17 - Groups, 18 - Projects, 19 - Milestones, 20 - Tasks, 21 - Discussions, 22 - Time tracking, 23 - Reports, 24 - Projects settings, 25 - General, 26 - Products, 27 - Rooms, 28 - OAuth]
    """

    """
    allowed enum values
    """
    None = 0
    Files = 1
    Folders = 2
    DocumentsSettings = 3
    Companies = 4
    Persons = 5
    Contacts = 6
    CrmTasks = 7
    Opportunities = 8
    Invoices = 9
    Cases = 10
    CommonCrmSettings = 11
    ContactsSettings = 12
    ContactTypes = 13
    InvoiceSettings = 14
    OtherCrmSettings = 15
    Users = 16
    Groups = 17
    Projects = 18
    Milestones = 19
    Tasks = 20
    Discussions = 21
    TimeTracking = 22
    Reports = 23
    ProjectsSettings = 24
    General = 25
    Products = 26
    Rooms = 27
    OAuth = 28

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of LocationType from a JSON string"""
        return cls(json.loads(json_str))


