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



# import apis into api package
from docspace_api_sdk.api.ApiKeys.api_keys_api import ApiKeysApi
from docspace_api_sdk.api.Authentication.authentication_api import AuthenticationApi
from docspace_api_sdk.api.Backup.backup_api import BackupApi
from docspace_api_sdk.api.Capabilities.capabilities_api import CapabilitiesApi
from docspace_api_sdk.api.Files.files_api import FilesApi
from docspace_api_sdk.api.Files.folders_api import FoldersApi
from docspace_api_sdk.api.Files.operations_api import OperationsApi
from docspace_api_sdk.api.Files.quota_api import QuotaApi
from docspace_api_sdk.api.Files.settings_api import SettingsApi
from docspace_api_sdk.api.Files.sharing_api import SharingApi
from docspace_api_sdk.api.Files.third_party_integration_api import ThirdPartyIntegrationApi
from docspace_api_sdk.api.Group.group_api import GroupApi
from docspace_api_sdk.api.Group.search_api import SearchApi
from docspace_api_sdk.api.Migration.migration_api import MigrationApi
from docspace_api_sdk.api.OAuth20.authorization_api import AuthorizationApi
from docspace_api_sdk.api.OAuth20.client_management_api import ClientManagementApi
from docspace_api_sdk.api.OAuth20.client_querying_api import ClientQueryingApi
from docspace_api_sdk.api.OAuth20.scope_management_api import ScopeManagementApi
from docspace_api_sdk.api.People.guests_api import GuestsApi
from docspace_api_sdk.api.People.password_api import PasswordApi
from docspace_api_sdk.api.People.photos_api import PhotosApi
from docspace_api_sdk.api.People.profiles_api import ProfilesApi
from docspace_api_sdk.api.People.quota_api import QuotaApi
from docspace_api_sdk.api.People.search_api import SearchApi
from docspace_api_sdk.api.People.theme_api import ThemeApi
from docspace_api_sdk.api.People.third_party_accounts_api import ThirdPartyAccountsApi
from docspace_api_sdk.api.People.user_data_api import UserDataApi
from docspace_api_sdk.api.People.user_status_api import UserStatusApi
from docspace_api_sdk.api.People.user_type_api import UserTypeApi
from docspace_api_sdk.api.Portal.guests_api import GuestsApi
from docspace_api_sdk.api.Portal.payment_api import PaymentApi
from docspace_api_sdk.api.Portal.quota_api import QuotaApi
from docspace_api_sdk.api.Portal.settings_api import SettingsApi
from docspace_api_sdk.api.Portal.users_api import UsersApi
from docspace_api_sdk.api.Rooms.rooms_api import RoomsApi
from docspace_api_sdk.api.Security.access_to_dev_tools_api import AccessToDevToolsApi
from docspace_api_sdk.api.Security.active_connections_api import ActiveConnectionsApi
from docspace_api_sdk.api.Security.audit_trail_data_api import AuditTrailDataApi
from docspace_api_sdk.api.Security.banners_visibility_api import BannersVisibilityApi
from docspace_api_sdk.api.Security.csp_api import CSPApi
from docspace_api_sdk.api.Security.firebase_api import FirebaseApi
from docspace_api_sdk.api.Security.login_history_api import LoginHistoryApi
from docspace_api_sdk.api.Security.o_auth2_api import OAuth2Api
from docspace_api_sdk.api.Security.smtp_settings_api import SMTPSettingsApi
from docspace_api_sdk.api.Settings.access_to_dev_tools_api import AccessToDevToolsApi
from docspace_api_sdk.api.Settings.authorization_api import AuthorizationApi
from docspace_api_sdk.api.Settings.banners_visibility_api import BannersVisibilityApi
from docspace_api_sdk.api.Settings.common_settings_api import CommonSettingsApi
from docspace_api_sdk.api.Settings.cookies_api import CookiesApi
from docspace_api_sdk.api.Settings.encryption_api import EncryptionApi
from docspace_api_sdk.api.Settings.greeting_settings_api import GreetingSettingsApi
from docspace_api_sdk.api.Settings.ip_restrictions_api import IPRestrictionsApi
from docspace_api_sdk.api.Settings.license_api import LicenseApi
from docspace_api_sdk.api.Settings.login_settings_api import LoginSettingsApi
from docspace_api_sdk.api.Settings.messages_api import MessagesApi
from docspace_api_sdk.api.Settings.notifications_api import NotificationsApi
from docspace_api_sdk.api.Settings.owner_api import OwnerApi
from docspace_api_sdk.api.Settings.quota_api import QuotaApi
from docspace_api_sdk.api.Settings.rebranding_api import RebrandingApi
from docspace_api_sdk.api.Settings.sso_api import SSOApi
from docspace_api_sdk.api.Settings.security_api import SecurityApi
from docspace_api_sdk.api.Settings.statistics_api import StatisticsApi
from docspace_api_sdk.api.Settings.storage_api import StorageApi
from docspace_api_sdk.api.Settings.tfa_settings_api import TFASettingsApi
from docspace_api_sdk.api.Settings.telegram_api import TelegramApi
from docspace_api_sdk.api.Settings.webhooks_api import WebhooksApi
from docspace_api_sdk.api.Settings.webplugins_api import WebpluginsApi
from docspace_api_sdk.api.ThirdParty.third_party_api import ThirdPartyApi

