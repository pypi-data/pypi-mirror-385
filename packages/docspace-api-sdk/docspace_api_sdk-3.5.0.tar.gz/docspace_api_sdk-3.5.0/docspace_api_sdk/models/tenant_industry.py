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


class TenantIndustry(int, Enum):
    """
    [0 - Other, 1 - Accounting, 2 - Advertising marketing PR, 3 - Banking, 4 - Consulting, 5 - Design, 6 - Education, 7 - Environment, 8 - Financial services, 9 - Health care, 10 - IT, 11 - Legal, 12 - Manufacturing, 13 - Public sector, 14 - Publishing, 15 - Retail sales, 16 - Telecommunications]
    """

    """
    allowed enum values
    """
    Other = 0
    Accounting = 1
    AdvertisingMarketingPR = 2
    Banking = 3
    Consulting = 4
    Design = 5
    Education = 6
    Environment = 7
    FinancialServices = 8
    HealthCare = 9
    IT = 10
    Legal = 11
    Manufacturing = 12
    PublicSector = 13
    Publishing = 14
    RetailSales = 15
    Telecommunications = 16

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TenantIndustry from a JSON string"""
        return cls(json.loads(json_str))


