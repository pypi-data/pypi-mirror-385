# docspace_api_sdk

The ONLYOFFICE DocSpace SDK for Python is a library that provides tools for integrating and managing DocSpace features within your applications. It simplifies interaction with the DocSpace API by offering ready-to-use methods and models.

For more information, please visit [https://helpdesk.onlyoffice.com/hc/en-us](https://helpdesk.onlyoffice.com/hc/en-us)

## Requirements

Python 3.9+

## Installation & Usage
### Using pip

If the Python package is hosted in a repository, you can install it directly using:

```sh
pip install git+https://github.com/ONLYOFFICE/docspace-api-sdk-python.git
```

If required, run with root permissions:

```bash
sudo pip install git+https://github.com/ONLYOFFICE/docspace-api-sdk-python.git
```

Then import the package:
```python
import docspace_api_sdk
```

### Using setuptools

Alternatively, you can install the package using [setuptools](http://pypi.python.org/pypi/setuptools):

```sh
python setup.py install --user
```

To install the package for all users, run the following command:

```bash
sudo python setup.py install
```

Then import the package:
```python
import docspace_api_sdk
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import docspace_api_sdk
from docspace_api_sdk.rest import ApiException
from pprint import pprint

configuration = docspace_api_sdk.Configuration(
    host = "https://your-docspace.onlyoffice.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): Bearer
configuration = docspace_api_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)


# Enter a context with an instance of the API client
with docspace_api_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = docspace_api_sdk.ApiKeysApi(api_client)
    create_api_key_request_dto = docspace_api_sdk.CreateApiKeyRequestDto() # CreateApiKeyRequestDto |  (optional)

    try:
        # Create a user API key
        api_response = api_instance.create_api_key(create_api_key_request_dto=create_api_key_request_dto)
        print("The response of ApiKeysApi->create_api_key:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ApiKeysApi->create_api_key: %s\n" % e)

```

<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="asc_auth_key"></a>
### asc_auth_key

- **Type**: API key
- **API key parameter name**: asc_auth_key
- **Location**: 

<a id="Basic"></a>
### Basic

- **Type**: HTTP basic authentication

<a id="Bearer"></a>
### Bearer

- **Type**: Bearer authentication (JWT)

<a id="ApiKeyBearer"></a>
### ApiKeyBearer

- **Type**: API key
- **API key parameter name**: ApiKeyBearer
- **Location**: HTTP header

<a id="OAuth2"></a>
### OAuth2

- **Type**: OAuth
- **Flow**: accessCode
- **Authorization URL**: {{authBaseUrl}}/oauth2/authorize
- **Token Url**: {{authBaseUrl}}/oauth2/token
- **Scopes**: 
 - **read**: Read access to protected resources
 - **write**: Write access to protected resources

<a id="OpenId"></a>
### OpenId

- **Type**: OpenId Connect
- **OpenId Connect URL**: {{authBaseUrl}}/.well-known/openid-configuration

<a id="x-signature"></a>
### x-signature

- **Type**: API key
- **API key parameter name**: x-signature
- **Location**: 


## Documentation for API Endpoints

All URIs are relative to *https://your-docspace.onlyoffice.com*

<details>
  <summary>ApiKeys</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>ApiKeysApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#create_api_key"><strong>create_api_key</strong></a></td>
        <td><strong>POST</strong> /api/2.0/keys</td>
        <td>Create a user API key</td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#delete_api_key"><strong>delete_api_key</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/keys/{keyId}</td>
        <td>Delete a user API key</td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#get_all_permissions"><strong>get_all_permissions</strong></a></td>
        <td><strong>GET</strong> /api/2.0/keys/permissions</td>
        <td>Get API key permissions</td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#get_api_key"><strong>get_api_key</strong></a></td>
        <td><strong>GET</strong> /api/2.0/keys/@self</td>
        <td>Get current user&#39;s API key</td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#get_api_keys"><strong>get_api_keys</strong></a></td>
        <td><strong>GET</strong> /api/2.0/keys</td>
        <td>Get current user&#39;s API keys</td>
      </tr>
      <tr>
        <td><a href="docs/ApiKeysApi.md#update_api_key"><strong>update_api_key</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/keys/{keyId}</td>
        <td>Update an API key</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Authentication</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>AuthenticationApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#authenticate_me"><strong>authenticate_me</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication</td>
        <td>Authenticate a user</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#authenticate_me_from_body_with_code"><strong>authenticate_me_from_body_with_code</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication/{code}</td>
        <td>Authenticate a user by code</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#check_confirm"><strong>check_confirm</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication/confirm</td>
        <td>Open confirmation email URL</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#get_is_authentificated"><strong>get_is_authentificated</strong></a></td>
        <td><strong>GET</strong> /api/2.0/authentication</td>
        <td>Check authentication</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#logout"><strong>logout</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication/logout</td>
        <td>Log out</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#save_mobile_phone"><strong>save_mobile_phone</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication/setphone</td>
        <td>Set a mobile phone</td>
      </tr>
      <tr>
        <td><a href="docs/AuthenticationApi.md#send_sms_code"><strong>send_sms_code</strong></a></td>
        <td><strong>POST</strong> /api/2.0/authentication/sendsms</td>
        <td>Send SMS code</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Backup</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>BackupApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#create_backup_schedule"><strong>create_backup_schedule</strong></a></td>
        <td><strong>POST</strong> /api/2.0/backup/createbackupschedule</td>
        <td>Create the backup schedule</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#delete_backup"><strong>delete_backup</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/backup/deletebackup/{id}</td>
        <td>Delete the backup</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#delete_backup_history"><strong>delete_backup_history</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/backup/deletebackuphistory</td>
        <td>Delete the backup history</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#delete_backup_schedule"><strong>delete_backup_schedule</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/backup/deletebackupschedule</td>
        <td>Delete the backup schedule</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_backup_history"><strong>get_backup_history</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getbackuphistory</td>
        <td>Get the backup history</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_backup_progress"><strong>get_backup_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getbackupprogress</td>
        <td>Get the backup progress</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_backup_schedule"><strong>get_backup_schedule</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getbackupschedule</td>
        <td>Get the backup schedule</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_backups_count"><strong>get_backups_count</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getbackupscount</td>
        <td>Get the number of backups</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_backups_service_state"><strong>get_backups_service_state</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getservicestate</td>
        <td>Get the backup service state</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#get_restore_progress"><strong>get_restore_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/backup/getrestoreprogress</td>
        <td>Get the restoring progress</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#start_backup"><strong>start_backup</strong></a></td>
        <td><strong>POST</strong> /api/2.0/backup/startbackup</td>
        <td>Start the backup</td>
      </tr>
      <tr>
        <td><a href="docs/BackupApi.md#start_backup_restore"><strong>start_backup_restore</strong></a></td>
        <td><strong>POST</strong> /api/2.0/backup/startrestore</td>
        <td>Start the restoring process</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Capabilities</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>CapabilitiesApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/CapabilitiesApi.md#get_portal_capabilities"><strong>get_portal_capabilities</strong></a></td>
        <td><strong>GET</strong> /api/2.0/capabilities</td>
        <td>Get portal capabilities</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Files</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>FilesApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#add_file_to_recent"><strong>add_file_to_recent</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/recent</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#add_templates"><strong>add_templates</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/templates</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#change_version_history"><strong>change_version_history</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/history</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#check_fill_form_draft"><strong>check_fill_form_draft</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/masterform/{fileId}/checkfillformdraft</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#copy_file_as"><strong>copy_file_as</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/copyas</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_edit_session"><strong>create_edit_session</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/edit_session</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_file"><strong>create_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/file</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_file_in_my_documents"><strong>create_file_in_my_documents</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/@my/file</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_file_primary_external_link"><strong>create_file_primary_external_link</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{id}/link</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_html_file"><strong>create_html_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/html</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_html_file_in_my_documents"><strong>create_html_file_in_my_documents</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/@my/html</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_text_file"><strong>create_text_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/text</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_text_file_in_my_documents"><strong>create_text_file_in_my_documents</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/@my/text</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#create_thumbnails"><strong>create_thumbnails</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/thumbnails</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#delete_file"><strong>delete_file</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/file/{fileId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#delete_recent"><strong>delete_recent</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/recent</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#delete_templates"><strong>delete_templates</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/templates</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_all_form_roles"><strong>get_all_form_roles</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/formroles</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_edit_diff_url"><strong>get_edit_diff_url</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/edit/diff</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_edit_history"><strong>get_edit_history</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/edit/history</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_file_history"><strong>get_file_history</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/log</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_file_info"><strong>get_file_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_file_links"><strong>get_file_links</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_file_primary_external_link"><strong>get_file_primary_external_link</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{id}/link</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_file_version_info"><strong>get_file_version_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/history</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_fill_result"><strong>get_fill_result</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/fillresult</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_presigned_file_uri"><strong>get_presigned_file_uri</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/presigned</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_presigned_uri"><strong>get_presigned_uri</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/presigneduri</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_protected_file_users"><strong>get_protected_file_users</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/protectusers</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#get_reference_data"><strong>get_reference_data</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/referencedata</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#is_form_pdf"><strong>is_form_pdf</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/isformpdf</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#lock_file"><strong>lock_file</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/lock</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#manage_form_filling"><strong>manage_form_filling</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/manageformfilling</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#open_edit_file"><strong>open_edit_file</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/openedit</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#restore_file_version"><strong>restore_file_version</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/restoreversion</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#save_editing_file_from_form"><strong>save_editing_file_from_form</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/saveediting</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#save_file_as_pdf"><strong>save_file_as_pdf</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{id}/saveaspdf</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#save_form_role_mapping"><strong>save_form_role_mapping</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/formrolemapping</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#set_custom_filter_tag"><strong>set_custom_filter_tag</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/customfilter</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#set_file_external_link"><strong>set_file_external_link</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#set_file_order"><strong>set_file_order</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/{fileId}/order</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#set_files_order"><strong>set_files_order</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/order</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#start_edit_file"><strong>start_edit_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/startedit</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#start_filling_file"><strong>start_filling_file</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/startfilling</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#toggle_file_favorite"><strong>toggle_file_favorite</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/favorites/{fileId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#track_edit_file"><strong>track_edit_file</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/trackeditfile</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFilesApi.md#update_file"><strong>update_file</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>FoldersApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#check_upload"><strong>check_upload</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/upload/check</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#create_folder"><strong>create_folder</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/folder/{folderId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#create_folder_primary_external_link"><strong>create_folder_primary_external_link</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/folder/{id}/link</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#create_report_folder_history"><strong>create_report_folder_history</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/folder/{folderId}/log/report</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#delete_folder"><strong>delete_folder</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/folder/{folderId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_favorites_folder"><strong>get_favorites_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@favorites</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_files_used_space"><strong>get_files_used_space</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/filesusedspace</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder"><strong>get_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/{folderId}/formfilter</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_by_folder_id"><strong>get_folder_by_folder_id</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/{folderId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_history"><strong>get_folder_history</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{folderId}/log</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_info"><strong>get_folder_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{folderId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_links"><strong>get_folder_links</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_path"><strong>get_folder_path</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{folderId}/path</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_primary_external_link"><strong>get_folder_primary_external_link</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{id}/link</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folder_recent"><strong>get_folder_recent</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/recent</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_folders"><strong>get_folders</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/{folderId}/subfolders</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_my_folder"><strong>get_my_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@my</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_new_folder_items"><strong>get_new_folder_items</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/{folderId}/news</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_privacy_folder"><strong>get_privacy_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@privacy</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_recent_folder"><strong>get_recent_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@recent</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_root_folders"><strong>get_root_folders</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@root</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#get_trash_folder"><strong>get_trash_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@trash</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#insert_file"><strong>insert_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/insert</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#insert_file_to_my_from_body"><strong>insert_file_to_my_from_body</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/@my/insert</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#rename_folder"><strong>rename_folder</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/folder/{folderId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#set_folder_order"><strong>set_folder_order</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/folder/{folderId}/order</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#set_folder_primary_external_link"><strong>set_folder_primary_external_link</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/folder/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#upload_file"><strong>upload_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/upload</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesFoldersApi.md#upload_file_to_my"><strong>upload_file_to_my</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/@my/upload</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>OperationsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#add_favorites"><strong>add_favorites</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/favorites</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#bulk_download"><strong>bulk_download</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/bulkdownload</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#check_conversion_status"><strong>check_conversion_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/checkconversion</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#check_move_or_copy_batch_items"><strong>check_move_or_copy_batch_items</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/fileops/move</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#check_move_or_copy_dest_folder"><strong>check_move_or_copy_dest_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/fileops/checkdestfolder</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#copy_batch_items"><strong>copy_batch_items</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/copy</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#create_upload_session"><strong>create_upload_session</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/{folderId}/upload/create_session</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#delete_batch_items"><strong>delete_batch_items</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/delete</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#delete_favorites_from_body"><strong>delete_favorites_from_body</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/favorites</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#delete_file_versions"><strong>delete_file_versions</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/deleteversion</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#duplicate_batch_items"><strong>duplicate_batch_items</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/duplicate</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#empty_trash"><strong>empty_trash</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/emptytrash</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#get_operation_statuses"><strong>get_operation_statuses</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/fileops</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#get_operation_statuses_by_type"><strong>get_operation_statuses_by_type</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/fileops/{operationType}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#mark_as_read"><strong>mark_as_read</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/markasread</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#move_batch_items"><strong>move_batch_items</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/move</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#start_file_conversion"><strong>start_file_conversion</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/checkconversion</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#terminate_tasks"><strong>terminate_tasks</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/fileops/terminate/{id}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesOperationsApi.md#update_file_comment"><strong>update_file_comment</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/comment</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>QuotaApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesQuotaApi.md#reset_room_quota"><strong>reset_room_quota</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/resetquota</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesQuotaApi.md#update_rooms_quota"><strong>update_rooms_quota</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/roomquota</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#change_access_to_thirdparty"><strong>change_access_to_thirdparty</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/thirdparty</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#change_automatically_clean_up"><strong>change_automatically_clean_up</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/autocleanup</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#change_default_access_rights"><strong>change_default_access_rights</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/dafaultaccessrights</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#change_delete_confirm"><strong>change_delete_confirm</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/changedeleteconfrim</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#change_download_zip_from_body"><strong>change_download_zip_from_body</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/downloadtargz</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#check_doc_service_url"><strong>check_doc_service_url</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/docservice</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#display_file_extension"><strong>display_file_extension</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/displayfileextension</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#display_recent"><strong>display_recent</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/displayrecent</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#external_share"><strong>external_share</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/external</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#external_share_social_media"><strong>external_share_social_media</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/externalsocialmedia</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#forcesave"><strong>forcesave</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/forcesave</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#get_automatically_clean_up"><strong>get_automatically_clean_up</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/settings/autocleanup</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#get_doc_service_url"><strong>get_doc_service_url</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/docservice</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#get_files_module"><strong>get_files_module</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/info</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#get_files_settings"><strong>get_files_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/settings</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#hide_confirm_cancel_operation"><strong>hide_confirm_cancel_operation</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/hideconfirmcanceloperation</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#hide_confirm_convert"><strong>hide_confirm_convert</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/hideconfirmconvert</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#hide_confirm_room_lifetime"><strong>hide_confirm_room_lifetime</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/hideconfirmroomlifetime</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#is_available_privacy_room_settings"><strong>is_available_privacy_room_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/@privacy/available</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#keep_new_file_name"><strong>keep_new_file_name</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/keepnewfilename</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#set_open_editor_in_same_tab"><strong>set_open_editor_in_same_tab</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/settings/openeditorinsametab</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#store_forcesave"><strong>store_forcesave</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/storeforcesave</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#store_original"><strong>store_original</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/storeoriginal</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSettingsApi.md#update_file_if_exist"><strong>update_file_if_exist</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/updateifexist</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SharingApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#apply_external_share_password"><strong>apply_external_share_password</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/share/{key}/password</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#change_file_owner"><strong>change_file_owner</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/owner</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_external_share_data"><strong>get_external_share_data</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/share/{key}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_file_security_info"><strong>get_file_security_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{id}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_folder_security_info"><strong>get_folder_security_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{id}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_groups_members_with_file_security"><strong>get_groups_members_with_file_security</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/group/{groupId}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_groups_members_with_folder_security"><strong>get_groups_members_with_folder_security</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/folder/{folderId}/group/{groupId}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_security_info"><strong>get_security_info</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#get_shared_users"><strong>get_shared_users</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/file/{fileId}/sharedusers</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#remove_security_info"><strong>remove_security_info</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#send_editor_notify"><strong>send_editor_notify</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/file/{fileId}/sendeditornotify</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#set_file_security_info"><strong>set_file_security_info</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/file/{fileId}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#set_folder_security_info"><strong>set_folder_security_info</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/folder/{folderId}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesSharingApi.md#set_security_info"><strong>set_security_info</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/share</td>
        <td></td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ThirdPartyIntegrationApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#delete_third_party"><strong>delete_third_party</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/thirdparty/{providerId}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#get_all_providers"><strong>get_all_providers</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/thirdparty/providers</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#get_backup_third_party_account"><strong>get_backup_third_party_account</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/thirdparty/backup</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#get_capabilities"><strong>get_capabilities</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/thirdparty/capabilities</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#get_common_third_party_folders"><strong>get_common_third_party_folders</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/thirdparty/common</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#get_third_party_accounts"><strong>get_third_party_accounts</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/thirdparty</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#save_third_party"><strong>save_third_party</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/thirdparty</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/FilesThirdPartyIntegrationApi.md#save_third_party_backup"><strong>save_third_party_backup</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/thirdparty/backup</td>
        <td></td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Group</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>GroupApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#add_group"><strong>add_group</strong></a></td>
        <td><strong>POST</strong> /api/2.0/group</td>
        <td>Add a new group</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#add_members_to"><strong>add_members_to</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/group/{id}/members</td>
        <td>Add group members</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#delete_group"><strong>delete_group</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/group/{id}</td>
        <td>Delete a group</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#get_group"><strong>get_group</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group/{id}</td>
        <td>Get a group</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#get_group_by_user_id"><strong>get_group_by_user_id</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group/user/{userid}</td>
        <td>Get user groups</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#get_groups"><strong>get_groups</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group</td>
        <td>Get groups</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#move_members_to"><strong>move_members_to</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/group/{fromId}/members/{toId}</td>
        <td>Move group members</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#remove_members_from"><strong>remove_members_from</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/group/{id}/members</td>
        <td>Remove group members</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#set_group_manager"><strong>set_group_manager</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/group/{id}/manager</td>
        <td>Set a group manager</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#set_members_to"><strong>set_members_to</strong></a></td>
        <td><strong>POST</strong> /api/2.0/group/{id}/members</td>
        <td>Replace group members</td>
      </tr>
      <tr>
        <td><a href="docs/GroupApi.md#update_group"><strong>update_group</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/group/{id}</td>
        <td>Update a group</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SearchApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/GroupSearchApi.md#get_groups_with_files_shared"><strong>get_groups_with_files_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group/file/{id}</td>
        <td>Get groups with file sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/GroupSearchApi.md#get_groups_with_folders_shared"><strong>get_groups_with_folders_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group/folder/{id}</td>
        <td>Get groups with folder sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/GroupSearchApi.md#get_groups_with_rooms_shared"><strong>get_groups_with_rooms_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/group/room/{id}</td>
        <td>Get groups with room sharing settings</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Migration</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>MigrationApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#cancel_migration"><strong>cancel_migration</strong></a></td>
        <td><strong>POST</strong> /api/2.0/migration/cancel</td>
        <td>Cancel migration</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#clear_migration"><strong>clear_migration</strong></a></td>
        <td><strong>POST</strong> /api/2.0/migration/clear</td>
        <td>Clear migration</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#finish_migration"><strong>finish_migration</strong></a></td>
        <td><strong>POST</strong> /api/2.0/migration/finish</td>
        <td>Finish migration</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#get_migration_logs"><strong>get_migration_logs</strong></a></td>
        <td><strong>GET</strong> /api/2.0/migration/logs</td>
        <td>Get migration logs</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#get_migration_status"><strong>get_migration_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/migration/status</td>
        <td>Get migration status</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#list_migrations"><strong>list_migrations</strong></a></td>
        <td><strong>GET</strong> /api/2.0/migration/list</td>
        <td>Get migrations</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#start_migration"><strong>start_migration</strong></a></td>
        <td><strong>POST</strong> /api/2.0/migration/migrate</td>
        <td>Start migration</td>
      </tr>
      <tr>
        <td><a href="docs/MigrationApi.md#upload_and_initialize_migration"><strong>upload_and_initialize_migration</strong></a></td>
        <td><strong>POST</strong> /api/2.0/migration/init/{migratorName}</td>
        <td>Upload and initialize migration</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>OAuth20</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>AuthorizationApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20AuthorizationApi.md#authorize_o_auth"><strong>authorize_o_auth</strong></a></td>
        <td><strong>GET</strong> /oauth2/authorize</td>
        <td>OAuth2 authorization endpoint</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20AuthorizationApi.md#exchange_token"><strong>exchange_token</strong></a></td>
        <td><strong>POST</strong> /oauth2/token</td>
        <td>OAuth2 token endpoint</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20AuthorizationApi.md#submit_consent"><strong>submit_consent</strong></a></td>
        <td><strong>POST</strong> /oauth2/authorize</td>
        <td>OAuth2 consent endpoint</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ClientManagementApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#change_activation"><strong>change_activation</strong></a></td>
        <td><strong>PATCH</strong> /api/2.0/clients/{clientId}/activation</td>
        <td>Change the client activation status</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#create_client"><strong>create_client</strong></a></td>
        <td><strong>POST</strong> /api/2.0/clients</td>
        <td>Create a new OAuth2 client</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#delete_client"><strong>delete_client</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/clients/{clientId}</td>
        <td>Delete an OAuth2 client</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#regenerate_secret"><strong>regenerate_secret</strong></a></td>
        <td><strong>PATCH</strong> /api/2.0/clients/{clientId}/regenerate</td>
        <td>Regenerate the client secret</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#revoke_user_client"><strong>revoke_user_client</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/clients/{clientId}/revoke</td>
        <td>Revoke client consent</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientManagementApi.md#update_client"><strong>update_client</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/clients/{clientId}</td>
        <td>Update an existing OAuth2 client</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ClientQueryingApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_client"><strong>get_client</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients/{clientId}</td>
        <td>Get client details</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_client_info"><strong>get_client_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients/{clientId}/info</td>
        <td>Get detailed client information</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_clients"><strong>get_clients</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients</td>
        <td>Get clients</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_clients_info"><strong>get_clients_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients/info</td>
        <td>Get detailed information of clients</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_consents"><strong>get_consents</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients/consents</td>
        <td>Get user consents</td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ClientQueryingApi.md#get_public_client_info"><strong>get_public_client_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/clients/{clientId}/public/info</td>
        <td>Get public client information</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ScopeManagementApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/OAuth20ScopeManagementApi.md#get_scopes"><strong>get_scopes</strong></a></td>
        <td><strong>GET</strong> /api/2.0/scopes</td>
        <td>Get available OAuth2 scopes</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>People</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>GuestsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleGuestsApi.md#approve_guest_share_link"><strong>approve_guest_share_link</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/guests/share/approve</td>
        <td>Approve a guest sharing link</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleGuestsApi.md#delete_guests"><strong>delete_guests</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/people/guests</td>
        <td>Delete guests</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>PasswordApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePasswordApi.md#change_user_password"><strong>change_user_password</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/{userid}/password</td>
        <td>Change a user password</td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePasswordApi.md#send_user_password"><strong>send_user_password</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/password</td>
        <td>Remind a user password</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>PhotosApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePhotosApi.md#create_member_photo_thumbnails"><strong>create_member_photo_thumbnails</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/{userid}/photo/thumbnails</td>
        <td>Create photo thumbnails</td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePhotosApi.md#delete_member_photo"><strong>delete_member_photo</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/people/{userid}/photo</td>
        <td>Delete a user photo</td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePhotosApi.md#get_member_photo"><strong>get_member_photo</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/{userid}/photo</td>
        <td>Get a user photo</td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePhotosApi.md#update_member_photo"><strong>update_member_photo</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/{userid}/photo</td>
        <td>Update a user photo</td>
      </tr>
      <tr>
        <td><a href="docs/PeoplePhotosApi.md#upload_member_photo"><strong>upload_member_photo</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/{userid}/photo</td>
        <td>Upload a user photo</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ProfilesApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#add_member"><strong>add_member</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people</td>
        <td>Add a user</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#delete_member"><strong>delete_member</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/people/{userid}</td>
        <td>Delete a user</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#delete_profile"><strong>delete_profile</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/people/@self</td>
        <td>Delete my profile</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#get_all_profiles"><strong>get_all_profiles</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people</td>
        <td>Get profiles</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#get_claims"><strong>get_claims</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/tokendiagnostics</td>
        <td>Get user claims</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#get_profile_by_email"><strong>get_profile_by_email</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/email</td>
        <td>Get a profile by user email</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#get_profile_by_user_id"><strong>get_profile_by_user_id</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/{userid}</td>
        <td>Get a profile by user ID</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#get_self_profile"><strong>get_self_profile</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/@self</td>
        <td>Get my profile</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#invite_users"><strong>invite_users</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/invite</td>
        <td>Invite users</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#remove_users"><strong>remove_users</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/delete</td>
        <td>Delete users</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#resend_user_invites"><strong>resend_user_invites</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/invite</td>
        <td>Resend activation emails</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#send_email_change_instructions"><strong>send_email_change_instructions</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/email</td>
        <td>Send instructions to change email</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#update_member"><strong>update_member</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/{userid}</td>
        <td>Update a user</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleProfilesApi.md#update_member_culture"><strong>update_member_culture</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/{userid}/culture</td>
        <td>Update a user culture code</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>QuotaApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleQuotaApi.md#reset_users_quota"><strong>reset_users_quota</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/resetquota</td>
        <td>Reset a user quota limit</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleQuotaApi.md#update_user_quota"><strong>update_user_quota</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/userquota</td>
        <td>Change a user quota limit</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SearchApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_accounts_entries_with_files_shared"><strong>get_accounts_entries_with_files_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/accounts/file/{id}/search</td>
        <td>Get account entries with file sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_accounts_entries_with_folders_shared"><strong>get_accounts_entries_with_folders_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/accounts/folder/{id}/search</td>
        <td>Get account entries with folder sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_accounts_entries_with_rooms_shared"><strong>get_accounts_entries_with_rooms_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/accounts/room/{id}/search</td>
        <td>Get account entries</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_search"><strong>get_search</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/@search/{query}</td>
        <td>Search users</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_simple_by_filter"><strong>get_simple_by_filter</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/simple/filter</td>
        <td>Search users by extended filter</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_users_with_files_shared"><strong>get_users_with_files_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/file/{id}</td>
        <td>Get users with file sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_users_with_folders_shared"><strong>get_users_with_folders_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/folder/{id}</td>
        <td>Get users with folder sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#get_users_with_room_shared"><strong>get_users_with_room_shared</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/room/{id}</td>
        <td>Get users with room sharing settings</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#search_users_by_extended_filter"><strong>search_users_by_extended_filter</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/filter</td>
        <td>Search users with detailed information by extended filter</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#search_users_by_query"><strong>search_users_by_query</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/search</td>
        <td>Search users (using query parameters)</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleSearchApi.md#search_users_by_status"><strong>search_users_by_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/status/{status}/search</td>
        <td>Search users by status filter</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ThemeApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThemeApi.md#change_portal_theme"><strong>change_portal_theme</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/theme</td>
        <td>Change the portal theme</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThemeApi.md#get_portal_theme"><strong>get_portal_theme</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/theme</td>
        <td>Get the portal theme</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ThirdPartyAccountsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThirdPartyAccountsApi.md#get_third_party_auth_providers"><strong>get_third_party_auth_providers</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/thirdparty/providers</td>
        <td>Get third-party accounts</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThirdPartyAccountsApi.md#link_third_party_account"><strong>link_third_party_account</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/thirdparty/linkaccount</td>
        <td>Link a third-pary account</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThirdPartyAccountsApi.md#signup_third_party_account"><strong>signup_third_party_account</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/thirdparty/signup</td>
        <td>Create a third-pary account</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleThirdPartyAccountsApi.md#unlink_third_party_account"><strong>unlink_third_party_account</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/people/thirdparty/unlinkaccount</td>
        <td>Unlink a third-pary account</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>UserDataApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#get_delete_personal_folder_progress"><strong>get_delete_personal_folder_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/delete/personal/progress</td>
        <td>Get the progress of deleting the personal folder</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#get_reassign_progress"><strong>get_reassign_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/reassign/progress/{userid}</td>
        <td>Get the reassignment progress</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#get_remove_progress"><strong>get_remove_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/remove/progress/{userid}</td>
        <td>Get the deletion progress</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#necessary_reassign"><strong>necessary_reassign</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/reassign/necessary</td>
        <td>Check data for reassignment need</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#send_instructions_to_delete"><strong>send_instructions_to_delete</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/self/delete</td>
        <td>Send the deletion instructions</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#start_delete_personal_folder"><strong>start_delete_personal_folder</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/delete/personal/start</td>
        <td>Delete the personal folder</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#start_reassign"><strong>start_reassign</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/reassign/start</td>
        <td>Start the data reassignment</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#start_remove"><strong>start_remove</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/remove/start</td>
        <td>Start the data deletion</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#terminate_reassign"><strong>terminate_reassign</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/reassign/terminate</td>
        <td>Terminate the data reassignment</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserDataApi.md#terminate_remove"><strong>terminate_remove</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/remove/terminate</td>
        <td>Terminate the data deletion</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>UserStatusApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserStatusApi.md#get_by_status"><strong>get_by_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/status/{status}</td>
        <td>Get profiles by status</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserStatusApi.md#update_user_activation_status"><strong>update_user_activation_status</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/activationstatus/{activationstatus}</td>
        <td>Set an activation status to the users</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserStatusApi.md#update_user_status"><strong>update_user_status</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/status/{status}</td>
        <td>Change a user status</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>UserTypeApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserTypeApi.md#get_user_type_update_progress"><strong>get_user_type_update_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/type/progress/{userid}</td>
        <td>Get the progress of updating user type</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserTypeApi.md#star_user_typet_update"><strong>star_user_typet_update</strong></a></td>
        <td><strong>POST</strong> /api/2.0/people/type</td>
        <td>Start updating user type</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserTypeApi.md#terminate_user_type_update"><strong>terminate_user_type_update</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/type/terminate</td>
        <td>Terminate updating user type</td>
      </tr>
      <tr>
        <td><a href="docs/PeopleUserTypeApi.md#update_user_type"><strong>update_user_type</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/people/type/{type}</td>
        <td>Change a user type</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Portal</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>GuestsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PortalGuestsApi.md#get_guest_sharing_link"><strong>get_guest_sharing_link</strong></a></td>
        <td><strong>GET</strong> /api/2.0/people/guests/{userid}/share</td>
        <td>Get a guest sharing link</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>PaymentApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#calculate_wallet_payment"><strong>calculate_wallet_payment</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/payment/calculatewallet</td>
        <td>Calculate the wallet payment amount</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#change_tenant_wallet_service_state"><strong>change_tenant_wallet_service_state</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/payment/servicestate</td>
        <td>Change wallet service state</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#create_customer_operations_report"><strong>create_customer_operations_report</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/payment/customer/operationsreport</td>
        <td>Start the customer operations report generation</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_checkout_setup_url"><strong>get_checkout_setup_url</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/chechoutsetupurl</td>
        <td>Get the checkout setup page URL</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_customer_balance"><strong>get_customer_balance</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/customer/balance</td>
        <td>Get the customer balance</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_customer_info"><strong>get_customer_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/customerinfo</td>
        <td>Get the customer information</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_customer_operations"><strong>get_customer_operations</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/customer/operations</td>
        <td>Get the customer operations</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_customer_operations_report"><strong>get_customer_operations_report</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/customer/operationsreport</td>
        <td>Get the status of the customer operations report generation</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_payment_account"><strong>get_payment_account</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/account</td>
        <td>Get the payment account</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_payment_currencies"><strong>get_payment_currencies</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/currencies</td>
        <td>Get currencies</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_payment_quotas"><strong>get_payment_quotas</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/quotas</td>
        <td>Get quotas</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_payment_url"><strong>get_payment_url</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/payment/url</td>
        <td>Get the payment page URL</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_portal_prices"><strong>get_portal_prices</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/prices</td>
        <td>Get prices</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_quota_payment_information"><strong>get_quota_payment_information</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/quota</td>
        <td>Get quota payment information</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_tenant_wallet_service_settings"><strong>get_tenant_wallet_service_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/servicessettings</td>
        <td>Get wallet services settings</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_tenant_wallet_settings"><strong>get_tenant_wallet_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/topupsettings</td>
        <td>Get wallet auto top-up settings</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_wallet_service"><strong>get_wallet_service</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/walletservice</td>
        <td>Get wallet service</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#get_wallet_services"><strong>get_wallet_services</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/payment/walletservices</td>
        <td>Get wallet services</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#send_payment_request"><strong>send_payment_request</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/payment/request</td>
        <td>Send a payment request</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#set_tenant_wallet_settings"><strong>set_tenant_wallet_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/payment/topupsettings</td>
        <td>Set wallet auto top-up settings</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#terminate_customer_operations_report"><strong>terminate_customer_operations_report</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/portal/payment/customer/operationsreport</td>
        <td>Terminate the customer operations report generation</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#top_up_deposit"><strong>top_up_deposit</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/payment/deposit</td>
        <td>Put money on deposit</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#update_payment"><strong>update_payment</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/payment/update</td>
        <td>Update the payment quantity</td>
      </tr>
      <tr>
        <td><a href="docs/PortalPaymentApi.md#update_wallet_payment"><strong>update_wallet_payment</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/payment/updatewallet</td>
        <td>Update the wallet payment quantity</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>QuotaApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PortalQuotaApi.md#get_portal_quota"><strong>get_portal_quota</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/quota</td>
        <td>Get a portal quota</td>
      </tr>
      <tr>
        <td><a href="docs/PortalQuotaApi.md#get_portal_tariff"><strong>get_portal_tariff</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/tariff</td>
        <td>Get a portal tariff</td>
      </tr>
      <tr>
        <td><a href="docs/PortalQuotaApi.md#get_portal_used_space"><strong>get_portal_used_space</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/usedspace</td>
        <td>Get the portal used space</td>
      </tr>
      <tr>
        <td><a href="docs/PortalQuotaApi.md#get_right_quota"><strong>get_right_quota</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/quota/right</td>
        <td>Get the recommended quota</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#continue_portal"><strong>continue_portal</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/continue</td>
        <td>Restore a portal</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#delete_portal"><strong>delete_portal</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/portal/delete</td>
        <td>Delete a portal</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#get_portal_information"><strong>get_portal_information</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal</td>
        <td>Get a portal</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#get_portal_path"><strong>get_portal_path</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/path</td>
        <td>Get a path to the portal</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#send_delete_instructions"><strong>send_delete_instructions</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/delete</td>
        <td>Send removal instructions</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#send_suspend_instructions"><strong>send_suspend_instructions</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/suspend</td>
        <td>Send suspension instructions</td>
      </tr>
      <tr>
        <td><a href="docs/PortalSettingsApi.md#suspend_portal"><strong>suspend_portal</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/portal/suspend</td>
        <td>Deactivate a portal</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>UsersApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/PortalUsersApi.md#get_invitation_link"><strong>get_invitation_link</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/users/invite/{employeeType}</td>
        <td>Get an invitation link</td>
      </tr>
      <tr>
        <td><a href="docs/PortalUsersApi.md#get_portal_users_count"><strong>get_portal_users_count</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/userscount</td>
        <td>Get a number of portal users</td>
      </tr>
      <tr>
        <td><a href="docs/PortalUsersApi.md#get_user_by_id"><strong>get_user_by_id</strong></a></td>
        <td><strong>GET</strong> /api/2.0/portal/users/{userID}</td>
        <td>Get a user by ID</td>
      </tr>
      <tr>
        <td><a href="docs/PortalUsersApi.md#mark_gift_message_as_read"><strong>mark_gift_message_as_read</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/present/mark</td>
        <td>Mark a gift message as read</td>
      </tr>
      <tr>
        <td><a href="docs/PortalUsersApi.md#send_congratulations"><strong>send_congratulations</strong></a></td>
        <td><strong>POST</strong> /api/2.0/portal/sendcongratulations</td>
        <td>Send congratulations</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Rooms</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>RoomsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#add_room_tags"><strong>add_room_tags</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/tags</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#archive_room"><strong>archive_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/archive</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#change_room_cover"><strong>change_room_cover</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/{id}/cover</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room"><strong>create_room</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room_from_template"><strong>create_room_from_template</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/fromtemplate</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room_logo"><strong>create_room_logo</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/{id}/logo</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room_tag"><strong>create_room_tag</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/tags</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room_template"><strong>create_room_template</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/roomtemplate</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#create_room_third_party"><strong>create_room_third_party</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/thirdparty/{id}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#delete_custom_tags"><strong>delete_custom_tags</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/tags</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#delete_room"><strong>delete_room</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/rooms/{id}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#delete_room_logo"><strong>delete_room_logo</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/rooms/{id}/logo</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#delete_room_tags"><strong>delete_room_tags</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/rooms/{id}/tags</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_new_room_items"><strong>get_new_room_items</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/{id}/news</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_public_settings"><strong>get_public_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/roomtemplate/{id}/public</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_covers"><strong>get_room_covers</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/covers</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_creating_status"><strong>get_room_creating_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/fromtemplate/status</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_index_export"><strong>get_room_index_export</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/indexexport</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_info"><strong>get_room_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/{id}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_links"><strong>get_room_links</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_security_info"><strong>get_room_security_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/{id}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_tags_info"><strong>get_room_tags_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/tags</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_room_template_creating_status"><strong>get_room_template_creating_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/roomtemplate/status</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_rooms_folder"><strong>get_rooms_folder</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_rooms_new_items"><strong>get_rooms_new_items</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/news</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#get_rooms_primary_external_link"><strong>get_rooms_primary_external_link</strong></a></td>
        <td><strong>GET</strong> /api/2.0/files/rooms/{id}/link</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#pin_room"><strong>pin_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/pin</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#reorder_room"><strong>reorder_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/reorder</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#resend_email_invitations"><strong>resend_email_invitations</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/{id}/resend</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#set_public_settings"><strong>set_public_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/roomtemplate/public</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#set_room_link"><strong>set_room_link</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/links</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#set_room_security"><strong>set_room_security</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/share</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#start_room_index_export"><strong>start_room_index_export</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/rooms/{id}/indexexport</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#terminate_room_index_export"><strong>terminate_room_index_export</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/files/rooms/indexexport</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#unarchive_room"><strong>unarchive_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/unarchive</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#unpin_room"><strong>unpin_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}/unpin</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#update_room"><strong>update_room</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/files/rooms/{id}</td>
        <td></td>
      </tr>
      <tr>
        <td><a href="docs/RoomsApi.md#upload_room_logo"><strong>upload_room_logo</strong></a></td>
        <td><strong>POST</strong> /api/2.0/files/logos</td>
        <td></td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Security</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>AccessToDevToolsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAccessToDevToolsApi.md#set_tenant_dev_tools_access_settings"><strong>set_tenant_dev_tools_access_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/devtoolsaccess</td>
        <td>Set the Developer Tools access settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>ActiveConnectionsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityActiveConnectionsApi.md#get_all_active_connections"><strong>get_all_active_connections</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/activeconnections</td>
        <td>Get active connections</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityActiveConnectionsApi.md#log_out_active_connection"><strong>log_out_active_connection</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/security/activeconnections/logout/{loginEventId}</td>
        <td>Log out from the connection</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityActiveConnectionsApi.md#log_out_all_active_connections_change_password"><strong>log_out_all_active_connections_change_password</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/security/activeconnections/logoutallchangepassword</td>
        <td>Log out and change password</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityActiveConnectionsApi.md#log_out_all_active_connections_for_user"><strong>log_out_all_active_connections_for_user</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/security/activeconnections/logoutall/{userId}</td>
        <td>Log out for the user by ID</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityActiveConnectionsApi.md#log_out_all_except_this_connection"><strong>log_out_all_except_this_connection</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/security/activeconnections/logoutallexceptthis</td>
        <td>Log out from all connections except the current one</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>AuditTrailDataApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#create_audit_trail_report"><strong>create_audit_trail_report</strong></a></td>
        <td><strong>POST</strong> /api/2.0/security/audit/events/report</td>
        <td>Generate the audit trail report</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#get_audit_events_by_filter"><strong>get_audit_events_by_filter</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/events/filter</td>
        <td>Get filtered audit trail data</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#get_audit_settings"><strong>get_audit_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/settings/lifetime</td>
        <td>Get the audit trail settings</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#get_audit_trail_mappers"><strong>get_audit_trail_mappers</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/mappers</td>
        <td>Get audit trail mappers</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#get_audit_trail_types"><strong>get_audit_trail_types</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/types</td>
        <td>Get audit trail types</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#get_last_audit_events"><strong>get_last_audit_events</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/events/last</td>
        <td>Get audit trail data</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityAuditTrailDataApi.md#set_audit_settings"><strong>set_audit_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/security/audit/settings/lifetime</td>
        <td>Set the audit trail settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>BannersVisibilityApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityBannersVisibilityApi.md#set_tenant_banner_settings"><strong>set_tenant_banner_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/banner</td>
        <td>Set the banners visibility</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>CSPApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityCSPApi.md#configure_csp"><strong>configure_csp</strong></a></td>
        <td><strong>POST</strong> /api/2.0/security/csp</td>
        <td>Configure CSP settings</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityCSPApi.md#get_csp_settings"><strong>get_csp_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/csp</td>
        <td>Get CSP settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>FirebaseApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityFirebaseApi.md#doc_register_pusn_notification_device"><strong>doc_register_pusn_notification_device</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/push/docregisterdevice</td>
        <td>Save the Documents Firebase device token</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityFirebaseApi.md#subscribe_documents_push_notification"><strong>subscribe_documents_push_notification</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/push/docsubscribe</td>
        <td>Subscribe to Documents push notification</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>LoginHistoryApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityLoginHistoryApi.md#create_login_history_report"><strong>create_login_history_report</strong></a></td>
        <td><strong>POST</strong> /api/2.0/security/audit/login/report</td>
        <td>Generate the login history report</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityLoginHistoryApi.md#get_last_login_events"><strong>get_last_login_events</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/login/last</td>
        <td>Get login history</td>
      </tr>
      <tr>
        <td><a href="docs/SecurityLoginHistoryApi.md#get_login_events_by_filter"><strong>get_login_events_by_filter</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/audit/login/filter</td>
        <td>Get filtered login events</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>OAuth2Api</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecurityOAuth2Api.md#generate_jwt_token"><strong>generate_jwt_token</strong></a></td>
        <td><strong>GET</strong> /api/2.0/security/oauth2/token</td>
        <td>Generate JWT token</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SMTPSettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SecuritySMTPSettingsApi.md#get_smtp_operation_status"><strong>get_smtp_operation_status</strong></a></td>
        <td><strong>GET</strong> /api/2.0/smtpsettings/smtp/test/status</td>
        <td>Get the SMTP testing process status</td>
      </tr>
      <tr>
        <td><a href="docs/SecuritySMTPSettingsApi.md#get_smtp_settings"><strong>get_smtp_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/smtpsettings/smtp</td>
        <td>Get the SMTP settings</td>
      </tr>
      <tr>
        <td><a href="docs/SecuritySMTPSettingsApi.md#reset_smtp_settings"><strong>reset_smtp_settings</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/smtpsettings/smtp</td>
        <td>Reset the SMTP settings</td>
      </tr>
      <tr>
        <td><a href="docs/SecuritySMTPSettingsApi.md#save_smtp_settings"><strong>save_smtp_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/smtpsettings/smtp</td>
        <td>Save the SMTP settings</td>
      </tr>
      <tr>
        <td><a href="docs/SecuritySMTPSettingsApi.md#test_smtp_settings"><strong>test_smtp_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/smtpsettings/smtp/test</td>
        <td>Test the SMTP settings</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>Settings</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>AccessToDevToolsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsAccessToDevToolsApi.md#get_tenant_access_dev_tools_settings"><strong>get_tenant_access_dev_tools_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/devtoolsaccess</td>
        <td>Get the Developer Tools access settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>AuthorizationApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsAuthorizationApi.md#get_auth_services"><strong>get_auth_services</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/authservice</td>
        <td>Get the authorization services</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsAuthorizationApi.md#save_auth_keys"><strong>save_auth_keys</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/authservice</td>
        <td>Save the authorization keys</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>BannersVisibilityApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsBannersVisibilityApi.md#get_tenant_banner_settings"><strong>get_tenant_banner_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/banner</td>
        <td>Get the banners visibility</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>CommonSettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#close_admin_helper"><strong>close_admin_helper</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/closeadminhelper</td>
        <td>Close the admin helper</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#complete_wizard"><strong>complete_wizard</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/wizard/complete</td>
        <td>Complete the Wizard settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#configure_deep_link"><strong>configure_deep_link</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/deeplink</td>
        <td>Configure the deep link settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#delete_portal_color_theme"><strong>delete_portal_color_theme</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/colortheme</td>
        <td>Delete a color theme</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_deep_link_settings"><strong>get_deep_link_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/deeplink</td>
        <td>Get the deep link settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_payment_settings"><strong>get_payment_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/payment</td>
        <td>Get the payment settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_portal_color_theme"><strong>get_portal_color_theme</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/colortheme</td>
        <td>Get a color theme</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_portal_hostname"><strong>get_portal_hostname</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/machine</td>
        <td>Get hostname</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_portal_logo"><strong>get_portal_logo</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/logo</td>
        <td>Get a portal logo</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_portal_settings"><strong>get_portal_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings</td>
        <td>Get the portal settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_socket_settings"><strong>get_socket_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/socket</td>
        <td>Get the socket settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_supported_cultures"><strong>get_supported_cultures</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/cultures</td>
        <td>Get supported languages</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_tenant_user_invitation_settings"><strong>get_tenant_user_invitation_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/invitationsettings</td>
        <td>Get the user invitation settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#get_time_zones"><strong>get_time_zones</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/timezones</td>
        <td>Get time zones</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#save_dns_settings"><strong>save_dns_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/dns</td>
        <td>Save the DNS settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#save_mail_domain_settings"><strong>save_mail_domain_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/maildomainsettings</td>
        <td>Save the mail domain settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#save_portal_color_theme"><strong>save_portal_color_theme</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/colortheme</td>
        <td>Save a color theme</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#update_email_activation_settings"><strong>update_email_activation_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/emailactivation</td>
        <td>Update the email activation settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCommonSettingsApi.md#update_invitation_settings"><strong>update_invitation_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/invitationsettings</td>
        <td>Update user invitation settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>CookiesApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCookiesApi.md#get_cookie_settings"><strong>get_cookie_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/cookiesettings</td>
        <td>Get cookies lifetime</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsCookiesApi.md#update_cookie_settings"><strong>update_cookie_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/cookiesettings</td>
        <td>Update cookies lifetime</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>EncryptionApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsEncryptionApi.md#get_storage_encryption_progress"><strong>get_storage_encryption_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/encryption/progress</td>
        <td>Get the storage encryption progress</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsEncryptionApi.md#get_storage_encryption_settings"><strong>get_storage_encryption_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/encryption/settings</td>
        <td>Get the storage encryption settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsEncryptionApi.md#start_storage_encryption"><strong>start_storage_encryption</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/encryption/start</td>
        <td>Start the storage encryption process</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>GreetingSettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsGreetingSettingsApi.md#get_greeting_settings"><strong>get_greeting_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/greetingsettings</td>
        <td>Get greeting settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsGreetingSettingsApi.md#get_is_default_greeting_settings"><strong>get_is_default_greeting_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/greetingsettings/isdefault</td>
        <td>Check the default greeting settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsGreetingSettingsApi.md#restore_greeting_settings"><strong>restore_greeting_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/greetingsettings/restore</td>
        <td>Restore the greeting settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsGreetingSettingsApi.md#save_greeting_settings"><strong>save_greeting_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/greetingsettings</td>
        <td>Save the greeting settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>IPRestrictionsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsIPRestrictionsApi.md#get_ip_restrictions"><strong>get_ip_restrictions</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/iprestrictions</td>
        <td>Get the IP portal restrictions</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsIPRestrictionsApi.md#read_ip_restrictions_settings"><strong>read_ip_restrictions_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/iprestrictions/settings</td>
        <td>Get the IP restriction settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsIPRestrictionsApi.md#save_ip_restrictions"><strong>save_ip_restrictions</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/iprestrictions</td>
        <td>Update the IP restrictions</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsIPRestrictionsApi.md#update_ip_restrictions_settings"><strong>update_ip_restrictions_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/iprestrictions/settings</td>
        <td>Update the IP restriction settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>LicenseApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLicenseApi.md#accept_license"><strong>accept_license</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/license/accept</td>
        <td>Activate a license</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLicenseApi.md#get_is_license_required"><strong>get_is_license_required</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/license/required</td>
        <td>Request a license</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLicenseApi.md#refresh_license"><strong>refresh_license</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/license/refresh</td>
        <td>Refresh the license</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLicenseApi.md#upload_license"><strong>upload_license</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/license</td>
        <td>Upload a license</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>LoginSettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLoginSettingsApi.md#get_login_settings"><strong>get_login_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/loginsettings</td>
        <td>Get the login settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLoginSettingsApi.md#set_default_login_settings"><strong>set_default_login_settings</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/security/loginsettings</td>
        <td>Reset the login settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsLoginSettingsApi.md#update_login_settings"><strong>update_login_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/security/loginsettings</td>
        <td>Update the login settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>MessagesApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsMessagesApi.md#enable_admin_message_settings"><strong>enable_admin_message_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/messagesettings</td>
        <td>Enable the administrator message settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsMessagesApi.md#send_admin_mail"><strong>send_admin_mail</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/sendadmmail</td>
        <td>Send a message to the administrator</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsMessagesApi.md#send_join_invite_mail"><strong>send_join_invite_mail</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/sendjoininvite</td>
        <td>Sends an invitation email</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>NotificationsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsNotificationsApi.md#get_notification_channels"><strong>get_notification_channels</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/notification/channels</td>
        <td>Get notification channels</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsNotificationsApi.md#get_notification_settings"><strong>get_notification_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/notification/{type}</td>
        <td>Check notification availability</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsNotificationsApi.md#get_rooms_notification_settings"><strong>get_rooms_notification_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/notification/rooms</td>
        <td>Get room notification settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsNotificationsApi.md#set_notification_settings"><strong>set_notification_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/notification</td>
        <td>Enable notifications</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsNotificationsApi.md#set_rooms_notification_status"><strong>set_rooms_notification_status</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/notification/rooms</td>
        <td>Set room notification status</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>OwnerApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsOwnerApi.md#send_owner_change_instructions"><strong>send_owner_change_instructions</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/owner</td>
        <td>Send the owner change instructions</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsOwnerApi.md#update_portal_owner"><strong>update_portal_owner</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/owner</td>
        <td>Update the portal owner</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>QuotaApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsQuotaApi.md#get_user_quota_settings"><strong>get_user_quota_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/userquotasettings</td>
        <td>Get the user quota settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsQuotaApi.md#save_room_quota_settings"><strong>save_room_quota_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/roomquotasettings</td>
        <td>Save the room quota settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsQuotaApi.md#set_tenant_quota_settings"><strong>set_tenant_quota_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/tenantquotasettings</td>
        <td>Save the tenant quota settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>RebrandingApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#delete_additional_white_label_settings"><strong>delete_additional_white_label_settings</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/rebranding/additional</td>
        <td>Delete the additional white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#delete_company_white_label_settings"><strong>delete_company_white_label_settings</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/rebranding/company</td>
        <td>Delete the company white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_additional_white_label_settings"><strong>get_additional_white_label_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/rebranding/additional</td>
        <td>Get the additional white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_company_white_label_settings"><strong>get_company_white_label_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/rebranding/company</td>
        <td>Get the company white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_enable_whitelabel"><strong>get_enable_whitelabel</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/enablewhitelabel</td>
        <td>Check the white label availability</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_is_default_white_label_logo_text"><strong>get_is_default_white_label_logo_text</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/whitelabel/logotext/isdefault</td>
        <td>Check the default white label logo text</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_is_default_white_label_logos"><strong>get_is_default_white_label_logos</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/whitelabel/logos/isdefault</td>
        <td>Check the default white label logos</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_licensor_data"><strong>get_licensor_data</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/companywhitelabel</td>
        <td>Get the licensor data</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_white_label_logo_text"><strong>get_white_label_logo_text</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/whitelabel/logotext</td>
        <td>Get the white label logo text</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#get_white_label_logos"><strong>get_white_label_logos</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/whitelabel/logos</td>
        <td>Get the white label logos</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#restore_white_label_logo_text"><strong>restore_white_label_logo_text</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/whitelabel/logotext/restore</td>
        <td>Restore the white label logo text</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#restore_white_label_logos"><strong>restore_white_label_logos</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/whitelabel/logos/restore</td>
        <td>Restore the white label logos</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#save_additional_white_label_settings"><strong>save_additional_white_label_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/rebranding/additional</td>
        <td>Save the additional white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#save_company_white_label_settings"><strong>save_company_white_label_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/rebranding/company</td>
        <td>Save the company white label settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#save_white_label_logo_text"><strong>save_white_label_logo_text</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/whitelabel/logotext/save</td>
        <td>Save the white label logo text settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#save_white_label_settings"><strong>save_white_label_settings</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/whitelabel/logos/save</td>
        <td>Save the white label logos</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsRebrandingApi.md#save_white_label_settings_from_files"><strong>save_white_label_settings_from_files</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/whitelabel/logos/savefromfiles</td>
        <td>Save the white label logos from files</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SSOApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSSOApi.md#get_default_sso_settings_v2"><strong>get_default_sso_settings_v2</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/ssov2/default</td>
        <td>Get the default SSO settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSSOApi.md#get_sso_settings_v2"><strong>get_sso_settings_v2</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/ssov2</td>
        <td>Get the SSO settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSSOApi.md#get_sso_settings_v2_constants"><strong>get_sso_settings_v2_constants</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/ssov2/constants</td>
        <td>Get the SSO settings constants</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSSOApi.md#reset_sso_settings_v2"><strong>reset_sso_settings_v2</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/ssov2</td>
        <td>Reset the SSO settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSSOApi.md#save_sso_settings_v2"><strong>save_sso_settings_v2</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/ssov2</td>
        <td>Save the SSO settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>SecurityApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_enabled_modules"><strong>get_enabled_modules</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/modules</td>
        <td>Get the enabled modules</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_is_product_administrator"><strong>get_is_product_administrator</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/administrator</td>
        <td>Check a product administrator</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_password_settings"><strong>get_password_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/password</td>
        <td>Get the password settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_product_administrators"><strong>get_product_administrators</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/administrator/{productid}</td>
        <td>Get the product administrators</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_web_item_security_info"><strong>get_web_item_security_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security/{id}</td>
        <td>Get the module availability</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#get_web_item_settings_security_info"><strong>get_web_item_settings_security_info</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/security</td>
        <td>Get the security settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#set_access_to_web_items"><strong>set_access_to_web_items</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/security/access</td>
        <td>Set the security settings to modules</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#set_product_administrator"><strong>set_product_administrator</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/security/administrator</td>
        <td>Set a product administrator</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#set_web_item_security"><strong>set_web_item_security</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/security</td>
        <td>Set the module security settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsSecurityApi.md#update_password_settings"><strong>update_password_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/security/password</td>
        <td>Set the password settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>StatisticsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStatisticsApi.md#get_space_usage_statistics"><strong>get_space_usage_statistics</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/statistics/spaceusage/{id}</td>
        <td>Get the space usage statistics</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>StorageApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#get_all_backup_storages"><strong>get_all_backup_storages</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/storage/backup</td>
        <td>Get the backup storages</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#get_all_cdn_storages"><strong>get_all_cdn_storages</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/storage/cdn</td>
        <td>Get the CDN storages</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#get_all_storages"><strong>get_all_storages</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/storage</td>
        <td>Get storages</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#get_amazon_s3_regions"><strong>get_amazon_s3_regions</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/storage/s3/regions</td>
        <td>Get Amazon regions</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#get_storage_progress"><strong>get_storage_progress</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/storage/progress</td>
        <td>Get the storage progress</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#reset_cdn_to_default"><strong>reset_cdn_to_default</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/storage/cdn</td>
        <td>Reset the CDN storage settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#reset_storage_to_default"><strong>reset_storage_to_default</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/storage</td>
        <td>Reset the storage settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#update_cdn_storage"><strong>update_cdn_storage</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/storage/cdn</td>
        <td>Update the CDN storage</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsStorageApi.md#update_storage"><strong>update_storage</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/storage</td>
        <td>Update a storage</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>TFASettingsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#get_tfa_app_codes"><strong>get_tfa_app_codes</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/tfaappcodes</td>
        <td>Get the TFA codes</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#get_tfa_confirm_url"><strong>get_tfa_confirm_url</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/tfaapp/confirm</td>
        <td>Get confirmation email</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#get_tfa_settings"><strong>get_tfa_settings</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/tfaapp</td>
        <td>Get the TFA settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#tfa_app_generate_setup_code"><strong>tfa_app_generate_setup_code</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/tfaapp/setup</td>
        <td>Generate setup code</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#tfa_validate_auth_code"><strong>tfa_validate_auth_code</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/tfaapp/validate</td>
        <td>Validate the TFA code</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#unlink_tfa_app"><strong>unlink_tfa_app</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/tfaappnewapp</td>
        <td>Unlink the TFA application</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#update_tfa_app_codes"><strong>update_tfa_app_codes</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/tfaappnewcodes</td>
        <td>Update the TFA codes</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#update_tfa_settings"><strong>update_tfa_settings</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/tfaapp</td>
        <td>Update the TFA settings</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTFASettingsApi.md#update_tfa_settings_link"><strong>update_tfa_settings_link</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/tfaappwithlink</td>
        <td>Get a confirmation email for updating TFA settings</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>TelegramApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTelegramApi.md#check_telegram"><strong>check_telegram</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/telegram/check</td>
        <td>Check the Telegram connection</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTelegramApi.md#link_telegram"><strong>link_telegram</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/telegram/link</td>
        <td>Get the Telegram link</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsTelegramApi.md#unlink_telegram"><strong>unlink_telegram</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/telegram/link</td>
        <td>Unlink Telegram</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>WebhooksApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#create_webhook"><strong>create_webhook</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/webhook</td>
        <td>Create a webhook</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#enable_webhook"><strong>enable_webhook</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/webhook/enable</td>
        <td>Enable a webhook</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#get_tenant_webhooks"><strong>get_tenant_webhooks</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/webhook</td>
        <td>Get webhooks</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#get_webhook_triggers"><strong>get_webhook_triggers</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/webhook/triggers</td>
        <td>Get webhook triggers</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#get_webhooks_logs"><strong>get_webhooks_logs</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/webhooks/log</td>
        <td>Get webhook logs</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#remove_webhook"><strong>remove_webhook</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/webhook/{id}</td>
        <td>Remove a webhook</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#retry_webhook"><strong>retry_webhook</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/webhook/{id}/retry</td>
        <td>Retry a webhook</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#retry_webhooks"><strong>retry_webhooks</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/webhook/retry</td>
        <td>Retry webhooks</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebhooksApi.md#update_webhook"><strong>update_webhook</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/webhook</td>
        <td>Update a webhook</td>
      </tr>
    <tr>
        <td colspan="3" style="text-align: center;"><strong>WebpluginsApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebpluginsApi.md#add_web_plugin_from_file"><strong>add_web_plugin_from_file</strong></a></td>
        <td><strong>POST</strong> /api/2.0/settings/webplugins</td>
        <td>Add a web plugin</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebpluginsApi.md#delete_web_plugin"><strong>delete_web_plugin</strong></a></td>
        <td><strong>DELETE</strong> /api/2.0/settings/webplugins/{name}</td>
        <td>Delete a web plugin</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebpluginsApi.md#get_web_plugin"><strong>get_web_plugin</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/webplugins/{name}</td>
        <td>Get a web plugin by name</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebpluginsApi.md#get_web_plugins"><strong>get_web_plugins</strong></a></td>
        <td><strong>GET</strong> /api/2.0/settings/webplugins</td>
        <td>Get web plugins</td>
      </tr>
      <tr>
        <td><a href="docs/SettingsWebpluginsApi.md#update_web_plugin"><strong>update_web_plugin</strong></a></td>
        <td><strong>PUT</strong> /api/2.0/settings/webplugins/{name}</td>
        <td>Update a web plugin</td>
      </tr>
    </tbody>
  </table>

</details>
<details>
  <summary>ThirdParty</summary>

  <table>
    <tbody>
      <tr>
        <th>Method</th>
        <th>HTTP request</th>
        <th>Description</th>
      </tr>
      <tr>
        <td colspan="3" style="text-align: center;"><strong>ThirdPartyApi</strong></td>
      </tr>
      <tr>
        <td><a href="docs/ThirdPartyApi.md#get_third_party_code"><strong>get_third_party_code</strong></a></td>
        <td><strong>GET</strong> /api/2.0/thirdparty/{provider}</td>
        <td>Get the code request</td>
      </tr>
    </tbody>
  </table>

</details>

## Documentation For Models

<details><summary>Models list</summary>

 - [AccountInfoArrayWrapper](docs/AccountInfoArrayWrapper.md)
 - [AccountInfoDto](docs/AccountInfoDto.md)
 - [AccountLoginType](docs/AccountLoginType.md)
 - [AceShortWrapper](docs/AceShortWrapper.md)
 - [AceShortWrapperArrayWrapper](docs/AceShortWrapperArrayWrapper.md)
 - [ActionConfig](docs/ActionConfig.md)
 - [ActionLinkConfig](docs/ActionLinkConfig.md)
 - [ActionType](docs/ActionType.md)
 - [ActiveConnectionsDto](docs/ActiveConnectionsDto.md)
 - [ActiveConnectionsItemDto](docs/ActiveConnectionsItemDto.md)
 - [ActiveConnectionsWrapper](docs/ActiveConnectionsWrapper.md)
 - [ActiveConnectionsWrapperLinksInner](docs/ActiveConnectionsWrapperLinksInner.md)
 - [AdditionalWhiteLabelSettings](docs/AdditionalWhiteLabelSettings.md)
 - [AdditionalWhiteLabelSettingsDto](docs/AdditionalWhiteLabelSettingsDto.md)
 - [AdditionalWhiteLabelSettingsWrapper](docs/AdditionalWhiteLabelSettingsWrapper.md)
 - [AdminMessageBaseSettingsRequestsDto](docs/AdminMessageBaseSettingsRequestsDto.md)
 - [AdminMessageSettingsRequestsDto](docs/AdminMessageSettingsRequestsDto.md)
 - [AnonymousConfigDto](docs/AnonymousConfigDto.md)
 - [ApiDateTime](docs/ApiDateTime.md)
 - [ApiKeyResponseArrayWrapper](docs/ApiKeyResponseArrayWrapper.md)
 - [ApiKeyResponseDto](docs/ApiKeyResponseDto.md)
 - [ApiKeyResponseWrapper](docs/ApiKeyResponseWrapper.md)
 - [ApplyFilterOption](docs/ApplyFilterOption.md)
 - [ArchiveRoomRequest](docs/ArchiveRoomRequest.md)
 - [Area](docs/Area.md)
 - [ArrayArrayWrapper](docs/ArrayArrayWrapper.md)
 - [AuditEventArrayWrapper](docs/AuditEventArrayWrapper.md)
 - [AuditEventDto](docs/AuditEventDto.md)
 - [AuthData](docs/AuthData.md)
 - [AuthKey](docs/AuthKey.md)
 - [AuthRequestsDto](docs/AuthRequestsDto.md)
 - [AuthServiceRequestsArrayWrapper](docs/AuthServiceRequestsArrayWrapper.md)
 - [AuthServiceRequestsDto](docs/AuthServiceRequestsDto.md)
 - [AuthenticationTokenDto](docs/AuthenticationTokenDto.md)
 - [AuthenticationTokenWrapper](docs/AuthenticationTokenWrapper.md)
 - [AutoCleanUpData](docs/AutoCleanUpData.md)
 - [AutoCleanUpDataWrapper](docs/AutoCleanUpDataWrapper.md)
 - [AutoCleanupRequestDto](docs/AutoCleanupRequestDto.md)
 - [BackupDto](docs/BackupDto.md)
 - [BackupHistoryRecord](docs/BackupHistoryRecord.md)
 - [BackupHistoryRecordArrayWrapper](docs/BackupHistoryRecordArrayWrapper.md)
 - [BackupPeriod](docs/BackupPeriod.md)
 - [BackupProgress](docs/BackupProgress.md)
 - [BackupProgressEnum](docs/BackupProgressEnum.md)
 - [BackupProgressWrapper](docs/BackupProgressWrapper.md)
 - [BackupRestoreDto](docs/BackupRestoreDto.md)
 - [BackupScheduleDto](docs/BackupScheduleDto.md)
 - [BackupServiceStateDto](docs/BackupServiceStateDto.md)
 - [BackupServiceStateWrapper](docs/BackupServiceStateWrapper.md)
 - [BackupStorageType](docs/BackupStorageType.md)
 - [Balance](docs/Balance.md)
 - [BalanceWrapper](docs/BalanceWrapper.md)
 - [BaseBatchRequestDto](docs/BaseBatchRequestDto.md)
 - [BaseBatchRequestDtoAllOfFileIds](docs/BaseBatchRequestDtoAllOfFileIds.md)
 - [BaseBatchRequestDtoAllOfFolderIds](docs/BaseBatchRequestDtoAllOfFolderIds.md)
 - [BaseStorageSettingsCdnStorageSettings](docs/BaseStorageSettingsCdnStorageSettings.md)
 - [BaseStorageSettingsStorageSettings](docs/BaseStorageSettingsStorageSettings.md)
 - [BatchRequestDto](docs/BatchRequestDto.md)
 - [BatchRequestDtoAllOfDestFolderId](docs/BatchRequestDtoAllOfDestFolderId.md)
 - [BatchRequestDtoAllOfFileIds](docs/BatchRequestDtoAllOfFileIds.md)
 - [BatchRequestDtoAllOfFolderIds](docs/BatchRequestDtoAllOfFolderIds.md)
 - [BatchTagsRequestDto](docs/BatchTagsRequestDto.md)
 - [BooleanWrapper](docs/BooleanWrapper.md)
 - [CapabilitiesDto](docs/CapabilitiesDto.md)
 - [CapabilitiesWrapper](docs/CapabilitiesWrapper.md)
 - [CdnStorageSettings](docs/CdnStorageSettings.md)
 - [CdnStorageSettingsWrapper](docs/CdnStorageSettingsWrapper.md)
 - [ChangeClientActivationRequest](docs/ChangeClientActivationRequest.md)
 - [ChangeHistory](docs/ChangeHistory.md)
 - [ChangeOwnerRequestDto](docs/ChangeOwnerRequestDto.md)
 - [ChangeWalletServiceStateRequestDto](docs/ChangeWalletServiceStateRequestDto.md)
 - [CheckConversionRequestDtoInteger](docs/CheckConversionRequestDtoInteger.md)
 - [CheckDestFolderDto](docs/CheckDestFolderDto.md)
 - [CheckDestFolderResult](docs/CheckDestFolderResult.md)
 - [CheckDestFolderWrapper](docs/CheckDestFolderWrapper.md)
 - [CheckDocServiceUrlRequestDto](docs/CheckDocServiceUrlRequestDto.md)
 - [CheckFillFormDraft](docs/CheckFillFormDraft.md)
 - [CheckUploadRequest](docs/CheckUploadRequest.md)
 - [ClientInfoResponse](docs/ClientInfoResponse.md)
 - [ClientResponse](docs/ClientResponse.md)
 - [ClientSecretResponse](docs/ClientSecretResponse.md)
 - [CoEditingConfig](docs/CoEditingConfig.md)
 - [CoEditingConfigMode](docs/CoEditingConfigMode.md)
 - [CompanyWhiteLabelSettings](docs/CompanyWhiteLabelSettings.md)
 - [CompanyWhiteLabelSettingsArrayWrapper](docs/CompanyWhiteLabelSettingsArrayWrapper.md)
 - [CompanyWhiteLabelSettingsDto](docs/CompanyWhiteLabelSettingsDto.md)
 - [CompanyWhiteLabelSettingsWrapper](docs/CompanyWhiteLabelSettingsWrapper.md)
 - [ConfigurationDtoInteger](docs/ConfigurationDtoInteger.md)
 - [ConfigurationIntegerWrapper](docs/ConfigurationIntegerWrapper.md)
 - [ConfirmData](docs/ConfirmData.md)
 - [ConfirmDto](docs/ConfirmDto.md)
 - [ConfirmType](docs/ConfirmType.md)
 - [ConfirmWrapper](docs/ConfirmWrapper.md)
 - [Contact](docs/Contact.md)
 - [ContentDisposition](docs/ContentDisposition.md)
 - [ContentType](docs/ContentType.md)
 - [ConversationResultArrayWrapper](docs/ConversationResultArrayWrapper.md)
 - [ConversationResultDto](docs/ConversationResultDto.md)
 - [CookieSettingsDto](docs/CookieSettingsDto.md)
 - [CookieSettingsRequestsDto](docs/CookieSettingsRequestsDto.md)
 - [CookieSettingsWrapper](docs/CookieSettingsWrapper.md)
 - [CopyAsJsonElement](docs/CopyAsJsonElement.md)
 - [CopyAsJsonElementDestFolderId](docs/CopyAsJsonElementDestFolderId.md)
 - [CoverRequestDto](docs/CoverRequestDto.md)
 - [CoversResultArrayWrapper](docs/CoversResultArrayWrapper.md)
 - [CoversResultDto](docs/CoversResultDto.md)
 - [CreateApiKeyRequestDto](docs/CreateApiKeyRequestDto.md)
 - [CreateClientRequest](docs/CreateClientRequest.md)
 - [CreateFileJsonElement](docs/CreateFileJsonElement.md)
 - [CreateFileJsonElementTemplateId](docs/CreateFileJsonElementTemplateId.md)
 - [CreateFolder](docs/CreateFolder.md)
 - [CreateRoomFromTemplateDto](docs/CreateRoomFromTemplateDto.md)
 - [CreateRoomRequestDto](docs/CreateRoomRequestDto.md)
 - [CreateTagRequestDto](docs/CreateTagRequestDto.md)
 - [CreateTextOrHtmlFile](docs/CreateTextOrHtmlFile.md)
 - [CreateThirdPartyRoom](docs/CreateThirdPartyRoom.md)
 - [CreateWebhooksConfigRequestsDto](docs/CreateWebhooksConfigRequestsDto.md)
 - [Cron](docs/Cron.md)
 - [CronParams](docs/CronParams.md)
 - [CspDto](docs/CspDto.md)
 - [CspRequestsDto](docs/CspRequestsDto.md)
 - [CspWrapper](docs/CspWrapper.md)
 - [Culture](docs/Culture.md)
 - [CultureSpecificExternalResource](docs/CultureSpecificExternalResource.md)
 - [CultureSpecificExternalResources](docs/CultureSpecificExternalResources.md)
 - [CurrenciesArrayWrapper](docs/CurrenciesArrayWrapper.md)
 - [CurrenciesDto](docs/CurrenciesDto.md)
 - [CurrentLicenseInfo](docs/CurrentLicenseInfo.md)
 - [CustomColorThemesSettingsColorItem](docs/CustomColorThemesSettingsColorItem.md)
 - [CustomColorThemesSettingsDto](docs/CustomColorThemesSettingsDto.md)
 - [CustomColorThemesSettingsItem](docs/CustomColorThemesSettingsItem.md)
 - [CustomColorThemesSettingsRequestsDto](docs/CustomColorThemesSettingsRequestsDto.md)
 - [CustomColorThemesSettingsWrapper](docs/CustomColorThemesSettingsWrapper.md)
 - [CustomFilterParameters](docs/CustomFilterParameters.md)
 - [CustomerConfigDto](docs/CustomerConfigDto.md)
 - [CustomerInfoDto](docs/CustomerInfoDto.md)
 - [CustomerInfoWrapper](docs/CustomerInfoWrapper.md)
 - [CustomerOperationsReportRequestDto](docs/CustomerOperationsReportRequestDto.md)
 - [CustomizationConfigDto](docs/CustomizationConfigDto.md)
 - [DarkThemeSettings](docs/DarkThemeSettings.md)
 - [DarkThemeSettingsRequestDto](docs/DarkThemeSettingsRequestDto.md)
 - [DarkThemeSettingsType](docs/DarkThemeSettingsType.md)
 - [DarkThemeSettingsWrapper](docs/DarkThemeSettingsWrapper.md)
 - [DateToAutoCleanUp](docs/DateToAutoCleanUp.md)
 - [DbTenant](docs/DbTenant.md)
 - [DbTenantPartner](docs/DbTenantPartner.md)
 - [DeepLinkConfigurationRequestsDto](docs/DeepLinkConfigurationRequestsDto.md)
 - [DeepLinkDto](docs/DeepLinkDto.md)
 - [DeepLinkHandlingMode](docs/DeepLinkHandlingMode.md)
 - [Delete](docs/Delete.md)
 - [DeleteBatchRequestDto](docs/DeleteBatchRequestDto.md)
 - [DeleteBatchRequestDtoAllOfFileIds](docs/DeleteBatchRequestDtoAllOfFileIds.md)
 - [DeleteBatchRequestDtoAllOfFolderIds](docs/DeleteBatchRequestDtoAllOfFolderIds.md)
 - [DeleteFolder](docs/DeleteFolder.md)
 - [DeleteRoomRequest](docs/DeleteRoomRequest.md)
 - [DeleteVersionBatchRequestDto](docs/DeleteVersionBatchRequestDto.md)
 - [DisplayRequestDto](docs/DisplayRequestDto.md)
 - [DistributedTaskStatus](docs/DistributedTaskStatus.md)
 - [DnsSettingsRequestsDto](docs/DnsSettingsRequestsDto.md)
 - [DocServiceUrlDto](docs/DocServiceUrlDto.md)
 - [DocServiceUrlWrapper](docs/DocServiceUrlWrapper.md)
 - [DocumentBuilderTaskDto](docs/DocumentBuilderTaskDto.md)
 - [DocumentBuilderTaskWrapper](docs/DocumentBuilderTaskWrapper.md)
 - [DocumentConfigDto](docs/DocumentConfigDto.md)
 - [DoubleWrapper](docs/DoubleWrapper.md)
 - [DownloadRequestDto](docs/DownloadRequestDto.md)
 - [DownloadRequestDtoAllOfFileIds](docs/DownloadRequestDtoAllOfFileIds.md)
 - [DownloadRequestDtoAllOfFolderIds](docs/DownloadRequestDtoAllOfFolderIds.md)
 - [DownloadRequestItemDto](docs/DownloadRequestItemDto.md)
 - [DownloadRequestItemDtoKey](docs/DownloadRequestItemDtoKey.md)
 - [DraftLocationInteger](docs/DraftLocationInteger.md)
 - [DuplicateRequestDto](docs/DuplicateRequestDto.md)
 - [DuplicateRequestDtoAllOfFileIds](docs/DuplicateRequestDtoAllOfFileIds.md)
 - [DuplicateRequestDtoAllOfFolderIds](docs/DuplicateRequestDtoAllOfFolderIds.md)
 - [EditHistoryArrayWrapper](docs/EditHistoryArrayWrapper.md)
 - [EditHistoryAuthor](docs/EditHistoryAuthor.md)
 - [EditHistoryChangesWrapper](docs/EditHistoryChangesWrapper.md)
 - [EditHistoryDataDto](docs/EditHistoryDataDto.md)
 - [EditHistoryDataWrapper](docs/EditHistoryDataWrapper.md)
 - [EditHistoryDto](docs/EditHistoryDto.md)
 - [EditHistoryUrl](docs/EditHistoryUrl.md)
 - [EditorConfigurationDto](docs/EditorConfigurationDto.md)
 - [EditorType](docs/EditorType.md)
 - [EmailActivationSettings](docs/EmailActivationSettings.md)
 - [EmailActivationSettingsWrapper](docs/EmailActivationSettingsWrapper.md)
 - [EmailInvitationDto](docs/EmailInvitationDto.md)
 - [EmailMemberRequestDto](docs/EmailMemberRequestDto.md)
 - [EmailValidationKeyModel](docs/EmailValidationKeyModel.md)
 - [EmbeddedConfig](docs/EmbeddedConfig.md)
 - [EmployeeActivationStatus](docs/EmployeeActivationStatus.md)
 - [EmployeeArrayWrapper](docs/EmployeeArrayWrapper.md)
 - [EmployeeDto](docs/EmployeeDto.md)
 - [EmployeeFullArrayWrapper](docs/EmployeeFullArrayWrapper.md)
 - [EmployeeFullDto](docs/EmployeeFullDto.md)
 - [EmployeeFullWrapper](docs/EmployeeFullWrapper.md)
 - [EmployeeStatus](docs/EmployeeStatus.md)
 - [EmployeeType](docs/EmployeeType.md)
 - [EmployeeWrapper](docs/EmployeeWrapper.md)
 - [EncryprtionStatus](docs/EncryprtionStatus.md)
 - [EncryptionKeysConfig](docs/EncryptionKeysConfig.md)
 - [EncryptionSettings](docs/EncryptionSettings.md)
 - [EncryptionSettingsWrapper](docs/EncryptionSettingsWrapper.md)
 - [EntryType](docs/EntryType.md)
 - [ErrorResponse](docs/ErrorResponse.md)
 - [ExchangeToken200Response](docs/ExchangeToken200Response.md)
 - [ExternalShareDto](docs/ExternalShareDto.md)
 - [ExternalShareRequestParam](docs/ExternalShareRequestParam.md)
 - [ExternalShareWrapper](docs/ExternalShareWrapper.md)
 - [FeatureUsedDto](docs/FeatureUsedDto.md)
 - [FeedbackConfig](docs/FeedbackConfig.md)
 - [FileConflictResolveType](docs/FileConflictResolveType.md)
 - [FileDtoInteger](docs/FileDtoInteger.md)
 - [FileDtoIntegerAllOfViewAccessibility](docs/FileDtoIntegerAllOfViewAccessibility.md)
 - [FileEntryBaseArrayWrapper](docs/FileEntryBaseArrayWrapper.md)
 - [FileEntryBaseDto](docs/FileEntryBaseDto.md)
 - [FileEntryBaseWrapper](docs/FileEntryBaseWrapper.md)
 - [FileEntryDtoInteger](docs/FileEntryDtoInteger.md)
 - [FileEntryDtoIntegerAllOfAvailableShareRights](docs/FileEntryDtoIntegerAllOfAvailableShareRights.md)
 - [FileEntryDtoIntegerAllOfSecurity](docs/FileEntryDtoIntegerAllOfSecurity.md)
 - [FileEntryDtoIntegerAllOfShareSettings](docs/FileEntryDtoIntegerAllOfShareSettings.md)
 - [FileEntryDtoString](docs/FileEntryDtoString.md)
 - [FileEntryIntegerArrayWrapper](docs/FileEntryIntegerArrayWrapper.md)
 - [FileEntryType](docs/FileEntryType.md)
 - [FileIntegerArrayWrapper](docs/FileIntegerArrayWrapper.md)
 - [FileIntegerWrapper](docs/FileIntegerWrapper.md)
 - [FileLink](docs/FileLink.md)
 - [FileLinkRequest](docs/FileLinkRequest.md)
 - [FileLinkWrapper](docs/FileLinkWrapper.md)
 - [FileOperationArrayWrapper](docs/FileOperationArrayWrapper.md)
 - [FileOperationDto](docs/FileOperationDto.md)
 - [FileOperationRequestBaseDto](docs/FileOperationRequestBaseDto.md)
 - [FileOperationType](docs/FileOperationType.md)
 - [FileOperationWrapper](docs/FileOperationWrapper.md)
 - [FileReference](docs/FileReference.md)
 - [FileReferenceData](docs/FileReferenceData.md)
 - [FileReferenceWrapper](docs/FileReferenceWrapper.md)
 - [FileShare](docs/FileShare.md)
 - [FileShareArrayWrapper](docs/FileShareArrayWrapper.md)
 - [FileShareDto](docs/FileShareDto.md)
 - [FileShareLink](docs/FileShareLink.md)
 - [FileShareParams](docs/FileShareParams.md)
 - [FileShareWrapper](docs/FileShareWrapper.md)
 - [FileStatus](docs/FileStatus.md)
 - [FileType](docs/FileType.md)
 - [FileUploadResultDto](docs/FileUploadResultDto.md)
 - [FileUploadResultWrapper](docs/FileUploadResultWrapper.md)
 - [FilesSettingsDto](docs/FilesSettingsDto.md)
 - [FilesSettingsDtoInternalFormats](docs/FilesSettingsDtoInternalFormats.md)
 - [FilesSettingsWrapper](docs/FilesSettingsWrapper.md)
 - [FilesStatisticsFolder](docs/FilesStatisticsFolder.md)
 - [FilesStatisticsResultDto](docs/FilesStatisticsResultDto.md)
 - [FilesStatisticsResultWrapper](docs/FilesStatisticsResultWrapper.md)
 - [FillingFormResultDtoInteger](docs/FillingFormResultDtoInteger.md)
 - [FillingFormResultIntegerWrapper](docs/FillingFormResultIntegerWrapper.md)
 - [FilterType](docs/FilterType.md)
 - [FinishDto](docs/FinishDto.md)
 - [FireBaseUser](docs/FireBaseUser.md)
 - [FireBaseUserWrapper](docs/FireBaseUserWrapper.md)
 - [FirebaseDto](docs/FirebaseDto.md)
 - [FirebaseRequestsDto](docs/FirebaseRequestsDto.md)
 - [FolderContentDtoInteger](docs/FolderContentDtoInteger.md)
 - [FolderContentIntegerArrayWrapper](docs/FolderContentIntegerArrayWrapper.md)
 - [FolderContentIntegerWrapper](docs/FolderContentIntegerWrapper.md)
 - [FolderDtoInteger](docs/FolderDtoInteger.md)
 - [FolderDtoString](docs/FolderDtoString.md)
 - [FolderIntegerArrayWrapper](docs/FolderIntegerArrayWrapper.md)
 - [FolderIntegerWrapper](docs/FolderIntegerWrapper.md)
 - [FolderLinkRequest](docs/FolderLinkRequest.md)
 - [FolderStringArrayWrapper](docs/FolderStringArrayWrapper.md)
 - [FolderStringWrapper](docs/FolderStringWrapper.md)
 - [FolderType](docs/FolderType.md)
 - [FormFillingManageAction](docs/FormFillingManageAction.md)
 - [FormFillingStatus](docs/FormFillingStatus.md)
 - [FormGalleryDto](docs/FormGalleryDto.md)
 - [FormRole](docs/FormRole.md)
 - [FormRoleArrayWrapper](docs/FormRoleArrayWrapper.md)
 - [FormRoleDto](docs/FormRoleDto.md)
 - [FormsItemArrayWrapper](docs/FormsItemArrayWrapper.md)
 - [FormsItemDto](docs/FormsItemDto.md)
 - [GetReferenceDataDtoInteger](docs/GetReferenceDataDtoInteger.md)
 - [GobackConfig](docs/GobackConfig.md)
 - [GreetingSettingsRequestsDto](docs/GreetingSettingsRequestsDto.md)
 - [GroupArrayWrapper](docs/GroupArrayWrapper.md)
 - [GroupDto](docs/GroupDto.md)
 - [GroupMemberSecurityRequestArrayWrapper](docs/GroupMemberSecurityRequestArrayWrapper.md)
 - [GroupMemberSecurityRequestDto](docs/GroupMemberSecurityRequestDto.md)
 - [GroupRequestDto](docs/GroupRequestDto.md)
 - [GroupSummaryArrayWrapper](docs/GroupSummaryArrayWrapper.md)
 - [GroupSummaryDto](docs/GroupSummaryDto.md)
 - [GroupWrapper](docs/GroupWrapper.md)
 - [HideConfirmConvertRequestDto](docs/HideConfirmConvertRequestDto.md)
 - [HistoryAction](docs/HistoryAction.md)
 - [HistoryArrayWrapper](docs/HistoryArrayWrapper.md)
 - [HistoryData](docs/HistoryData.md)
 - [HistoryDto](docs/HistoryDto.md)
 - [ICompressWrapper](docs/ICompressWrapper.md)
 - [IMagickGeometry](docs/IMagickGeometry.md)
 - [IPRestriction](docs/IPRestriction.md)
 - [IPRestrictionArrayWrapper](docs/IPRestrictionArrayWrapper.md)
 - [IPRestrictionsSettings](docs/IPRestrictionsSettings.md)
 - [IPRestrictionsSettingsWrapper](docs/IPRestrictionsSettingsWrapper.md)
 - [ImportableApiEntity](docs/ImportableApiEntity.md)
 - [InfoConfigDto](docs/InfoConfigDto.md)
 - [Int32Wrapper](docs/Int32Wrapper.md)
 - [Int64Wrapper](docs/Int64Wrapper.md)
 - [InviteUsersRequestDto](docs/InviteUsersRequestDto.md)
 - [IpRestrictionBase](docs/IpRestrictionBase.md)
 - [IpRestrictionsDto](docs/IpRestrictionsDto.md)
 - [IpRestrictionsWrapper](docs/IpRestrictionsWrapper.md)
 - [IsDefaultWhiteLabelLogosArrayWrapper](docs/IsDefaultWhiteLabelLogosArrayWrapper.md)
 - [IsDefaultWhiteLabelLogosDto](docs/IsDefaultWhiteLabelLogosDto.md)
 - [IsDefaultWhiteLabelLogosWrapper](docs/IsDefaultWhiteLabelLogosWrapper.md)
 - [ItemKeyValuePairObjectObject](docs/ItemKeyValuePairObjectObject.md)
 - [ItemKeyValuePairStringBoolean](docs/ItemKeyValuePairStringBoolean.md)
 - [ItemKeyValuePairStringLogoRequestsDto](docs/ItemKeyValuePairStringLogoRequestsDto.md)
 - [ItemKeyValuePairStringString](docs/ItemKeyValuePairStringString.md)
 - [KeyValuePairBooleanString](docs/KeyValuePairBooleanString.md)
 - [KeyValuePairBooleanStringWrapper](docs/KeyValuePairBooleanStringWrapper.md)
 - [KeyValuePairStringStringValues](docs/KeyValuePairStringStringValues.md)
 - [LinkAccountRequestDto](docs/LinkAccountRequestDto.md)
 - [LinkType](docs/LinkType.md)
 - [Location](docs/Location.md)
 - [LocationType](docs/LocationType.md)
 - [LockFileParameters](docs/LockFileParameters.md)
 - [LoginEventArrayWrapper](docs/LoginEventArrayWrapper.md)
 - [LoginEventDto](docs/LoginEventDto.md)
 - [LoginProvider](docs/LoginProvider.md)
 - [LoginSettingsDto](docs/LoginSettingsDto.md)
 - [LoginSettingsRequestDto](docs/LoginSettingsRequestDto.md)
 - [LoginSettingsWrapper](docs/LoginSettingsWrapper.md)
 - [Logo](docs/Logo.md)
 - [LogoConfigDto](docs/LogoConfigDto.md)
 - [LogoCover](docs/LogoCover.md)
 - [LogoRequest](docs/LogoRequest.md)
 - [LogoRequestsDto](docs/LogoRequestsDto.md)
 - [MailDomainSettingsRequestsDto](docs/MailDomainSettingsRequestsDto.md)
 - [ManageFormFillingDtoInteger](docs/ManageFormFillingDtoInteger.md)
 - [MemberBaseRequestDto](docs/MemberBaseRequestDto.md)
 - [MemberRequestDto](docs/MemberRequestDto.md)
 - [MembersRequest](docs/MembersRequest.md)
 - [MentionMessageWrapper](docs/MentionMessageWrapper.md)
 - [MentionWrapper](docs/MentionWrapper.md)
 - [MentionWrapperArrayWrapper](docs/MentionWrapperArrayWrapper.md)
 - [MessageAction](docs/MessageAction.md)
 - [MigratingApiFiles](docs/MigratingApiFiles.md)
 - [MigratingApiGroup](docs/MigratingApiGroup.md)
 - [MigratingApiUser](docs/MigratingApiUser.md)
 - [MigrationApiInfo](docs/MigrationApiInfo.md)
 - [MigrationStatusDto](docs/MigrationStatusDto.md)
 - [MigrationStatusWrapper](docs/MigrationStatusWrapper.md)
 - [MobilePhoneActivationStatus](docs/MobilePhoneActivationStatus.md)
 - [MobileRequestsDto](docs/MobileRequestsDto.md)
 - [Module](docs/Module.md)
 - [ModuleWrapper](docs/ModuleWrapper.md)
 - [NewItemsDtoFileEntryBaseDto](docs/NewItemsDtoFileEntryBaseDto.md)
 - [NewItemsDtoRoomNewItemsDto](docs/NewItemsDtoRoomNewItemsDto.md)
 - [NewItemsFileEntryBaseArrayWrapper](docs/NewItemsFileEntryBaseArrayWrapper.md)
 - [NewItemsRoomNewItemsArrayWrapper](docs/NewItemsRoomNewItemsArrayWrapper.md)
 - [NoContentResult](docs/NoContentResult.md)
 - [NoContentResultWrapper](docs/NoContentResultWrapper.md)
 - [NotificationChannelDto](docs/NotificationChannelDto.md)
 - [NotificationChannelStatusDto](docs/NotificationChannelStatusDto.md)
 - [NotificationChannelStatusWrapper](docs/NotificationChannelStatusWrapper.md)
 - [NotificationSettingsDto](docs/NotificationSettingsDto.md)
 - [NotificationSettingsRequestsDto](docs/NotificationSettingsRequestsDto.md)
 - [NotificationSettingsWrapper](docs/NotificationSettingsWrapper.md)
 - [NotificationType](docs/NotificationType.md)
 - [OAuth20Token](docs/OAuth20Token.md)
 - [ObjectArrayWrapper](docs/ObjectArrayWrapper.md)
 - [ObjectWrapper](docs/ObjectWrapper.md)
 - [OperationDto](docs/OperationDto.md)
 - [Options](docs/Options.md)
 - [OrderBy](docs/OrderBy.md)
 - [OrderRequestDto](docs/OrderRequestDto.md)
 - [OrdersItemRequestDtoInteger](docs/OrdersItemRequestDtoInteger.md)
 - [OrdersRequestDtoInteger](docs/OrdersRequestDtoInteger.md)
 - [OwnerChangeInstructionsDto](docs/OwnerChangeInstructionsDto.md)
 - [OwnerChangeInstructionsWrapper](docs/OwnerChangeInstructionsWrapper.md)
 - [OwnerIdSettingsRequestDto](docs/OwnerIdSettingsRequestDto.md)
 - [PageableModificationResponse](docs/PageableModificationResponse.md)
 - [PageableResponse](docs/PageableResponse.md)
 - [PageableResponseClientInfoResponse](docs/PageableResponseClientInfoResponse.md)
 - [Paragraph](docs/Paragraph.md)
 - [PasswordHasher](docs/PasswordHasher.md)
 - [PasswordSettingsDto](docs/PasswordSettingsDto.md)
 - [PasswordSettingsRequestsDto](docs/PasswordSettingsRequestsDto.md)
 - [PasswordSettingsWrapper](docs/PasswordSettingsWrapper.md)
 - [PaymentCalculation](docs/PaymentCalculation.md)
 - [PaymentCalculationWrapper](docs/PaymentCalculationWrapper.md)
 - [PaymentMethodStatus](docs/PaymentMethodStatus.md)
 - [PaymentSettingsDto](docs/PaymentSettingsDto.md)
 - [PaymentSettingsWrapper](docs/PaymentSettingsWrapper.md)
 - [PaymentUrlRequestsDto](docs/PaymentUrlRequestsDto.md)
 - [Payments](docs/Payments.md)
 - [PermissionsConfig](docs/PermissionsConfig.md)
 - [PluginsConfig](docs/PluginsConfig.md)
 - [PluginsDto](docs/PluginsDto.md)
 - [PriceDto](docs/PriceDto.md)
 - [ProductAdministratorDto](docs/ProductAdministratorDto.md)
 - [ProductAdministratorWrapper](docs/ProductAdministratorWrapper.md)
 - [ProductQuantityType](docs/ProductQuantityType.md)
 - [ProductType](docs/ProductType.md)
 - [ProviderArrayWrapper](docs/ProviderArrayWrapper.md)
 - [ProviderDto](docs/ProviderDto.md)
 - [ProviderFilter](docs/ProviderFilter.md)
 - [QuantityRequestDto](docs/QuantityRequestDto.md)
 - [Quota](docs/Quota.md)
 - [QuotaArrayWrapper](docs/QuotaArrayWrapper.md)
 - [QuotaDto](docs/QuotaDto.md)
 - [QuotaFilter](docs/QuotaFilter.md)
 - [QuotaSettingsRequestsDto](docs/QuotaSettingsRequestsDto.md)
 - [QuotaSettingsRequestsDtoDefaultQuota](docs/QuotaSettingsRequestsDtoDefaultQuota.md)
 - [QuotaState](docs/QuotaState.md)
 - [QuotaWrapper](docs/QuotaWrapper.md)
 - [RecaptchaType](docs/RecaptchaType.md)
 - [RecentConfig](docs/RecentConfig.md)
 - [RegStatus](docs/RegStatus.md)
 - [ReportDto](docs/ReportDto.md)
 - [ReportWrapper](docs/ReportWrapper.md)
 - [ReviewConfig](docs/ReviewConfig.md)
 - [RoomDataLifetimeDto](docs/RoomDataLifetimeDto.md)
 - [RoomDataLifetimePeriod](docs/RoomDataLifetimePeriod.md)
 - [RoomFromTemplateStatusDto](docs/RoomFromTemplateStatusDto.md)
 - [RoomFromTemplateStatusWrapper](docs/RoomFromTemplateStatusWrapper.md)
 - [RoomInvitation](docs/RoomInvitation.md)
 - [RoomInvitationRequest](docs/RoomInvitationRequest.md)
 - [RoomLinkRequest](docs/RoomLinkRequest.md)
 - [RoomNewItemsDto](docs/RoomNewItemsDto.md)
 - [RoomSecurityDto](docs/RoomSecurityDto.md)
 - [RoomSecurityError](docs/RoomSecurityError.md)
 - [RoomSecurityWrapper](docs/RoomSecurityWrapper.md)
 - [RoomTemplateDto](docs/RoomTemplateDto.md)
 - [RoomTemplateStatusDto](docs/RoomTemplateStatusDto.md)
 - [RoomTemplateStatusWrapper](docs/RoomTemplateStatusWrapper.md)
 - [RoomType](docs/RoomType.md)
 - [RoomsNotificationSettingsDto](docs/RoomsNotificationSettingsDto.md)
 - [RoomsNotificationSettingsWrapper](docs/RoomsNotificationSettingsWrapper.md)
 - [RoomsNotificationsSettingsRequestDto](docs/RoomsNotificationsSettingsRequestDto.md)
 - [Run](docs/Run.md)
 - [STRINGArrayWrapper](docs/STRINGArrayWrapper.md)
 - [SalesRequestsDto](docs/SalesRequestsDto.md)
 - [SaveAsPdfInteger](docs/SaveAsPdfInteger.md)
 - [SaveFormRoleMappingDtoInteger](docs/SaveFormRoleMappingDtoInteger.md)
 - [ScheduleDto](docs/ScheduleDto.md)
 - [ScheduleWrapper](docs/ScheduleWrapper.md)
 - [ScopeResponse](docs/ScopeResponse.md)
 - [SearchArea](docs/SearchArea.md)
 - [SecurityArrayWrapper](docs/SecurityArrayWrapper.md)
 - [SecurityDto](docs/SecurityDto.md)
 - [SecurityInfoRequestDto](docs/SecurityInfoRequestDto.md)
 - [SecurityInfoSimpleRequestDto](docs/SecurityInfoSimpleRequestDto.md)
 - [SecurityRequestsDto](docs/SecurityRequestsDto.md)
 - [SessionRequest](docs/SessionRequest.md)
 - [SetManagerRequest](docs/SetManagerRequest.md)
 - [SetPublicDto](docs/SetPublicDto.md)
 - [SettingsDto](docs/SettingsDto.md)
 - [SettingsRequestDto](docs/SettingsRequestDto.md)
 - [SettingsWrapper](docs/SettingsWrapper.md)
 - [SetupCode](docs/SetupCode.md)
 - [SetupCodeWrapper](docs/SetupCodeWrapper.md)
 - [SexEnum](docs/SexEnum.md)
 - [ShareFilterType](docs/ShareFilterType.md)
 - [SignupAccountRequestDto](docs/SignupAccountRequestDto.md)
 - [SmtpOperationStatusRequestsDto](docs/SmtpOperationStatusRequestsDto.md)
 - [SmtpOperationStatusRequestsWrapper](docs/SmtpOperationStatusRequestsWrapper.md)
 - [SmtpSettingsDto](docs/SmtpSettingsDto.md)
 - [SmtpSettingsWrapper](docs/SmtpSettingsWrapper.md)
 - [SortOrder](docs/SortOrder.md)
 - [SortedByType](docs/SortedByType.md)
 - [SsoCertificate](docs/SsoCertificate.md)
 - [SsoFieldMapping](docs/SsoFieldMapping.md)
 - [SsoIdpCertificateAdvanced](docs/SsoIdpCertificateAdvanced.md)
 - [SsoIdpSettings](docs/SsoIdpSettings.md)
 - [SsoSettingsRequestsDto](docs/SsoSettingsRequestsDto.md)
 - [SsoSettingsV2](docs/SsoSettingsV2.md)
 - [SsoSettingsV2Wrapper](docs/SsoSettingsV2Wrapper.md)
 - [SsoSpCertificateAdvanced](docs/SsoSpCertificateAdvanced.md)
 - [StartEdit](docs/StartEdit.md)
 - [StartFillingForm](docs/StartFillingForm.md)
 - [StartFillingMode](docs/StartFillingMode.md)
 - [StartReassignRequestDto](docs/StartReassignRequestDto.md)
 - [StartUpdateUserTypeDto](docs/StartUpdateUserTypeDto.md)
 - [Status](docs/Status.md)
 - [StatusCodeResult](docs/StatusCodeResult.md)
 - [StorageArrayWrapper](docs/StorageArrayWrapper.md)
 - [StorageDto](docs/StorageDto.md)
 - [StorageEncryptionRequestsDto](docs/StorageEncryptionRequestsDto.md)
 - [StorageFilter](docs/StorageFilter.md)
 - [StorageRequestsDto](docs/StorageRequestsDto.md)
 - [StorageSettings](docs/StorageSettings.md)
 - [StorageSettingsWrapper](docs/StorageSettingsWrapper.md)
 - [StringWrapper](docs/StringWrapper.md)
 - [SubAccount](docs/SubAccount.md)
 - [SubjectFilter](docs/SubjectFilter.md)
 - [SubjectType](docs/SubjectType.md)
 - [SubmitForm](docs/SubmitForm.md)
 - [Tariff](docs/Tariff.md)
 - [TariffState](docs/TariffState.md)
 - [TariffWrapper](docs/TariffWrapper.md)
 - [TaskProgressResponseDto](docs/TaskProgressResponseDto.md)
 - [TaskProgressResponseWrapper](docs/TaskProgressResponseWrapper.md)
 - [TelegramStatusDto](docs/TelegramStatusDto.md)
 - [TelegramStatusWrapper](docs/TelegramStatusWrapper.md)
 - [TemplatesConfig](docs/TemplatesConfig.md)
 - [TemplatesRequestDto](docs/TemplatesRequestDto.md)
 - [TenantAuditSettings](docs/TenantAuditSettings.md)
 - [TenantAuditSettingsWrapper](docs/TenantAuditSettingsWrapper.md)
 - [TenantBannerSettings](docs/TenantBannerSettings.md)
 - [TenantBannerSettingsDto](docs/TenantBannerSettingsDto.md)
 - [TenantBannerSettingsWrapper](docs/TenantBannerSettingsWrapper.md)
 - [TenantDeepLinkSettings](docs/TenantDeepLinkSettings.md)
 - [TenantDeepLinkSettingsWrapper](docs/TenantDeepLinkSettingsWrapper.md)
 - [TenantDevToolsAccessSettings](docs/TenantDevToolsAccessSettings.md)
 - [TenantDevToolsAccessSettingsDto](docs/TenantDevToolsAccessSettingsDto.md)
 - [TenantDevToolsAccessSettingsWrapper](docs/TenantDevToolsAccessSettingsWrapper.md)
 - [TenantDomainValidator](docs/TenantDomainValidator.md)
 - [TenantDto](docs/TenantDto.md)
 - [TenantEntityQuotaSettings](docs/TenantEntityQuotaSettings.md)
 - [TenantIndustry](docs/TenantIndustry.md)
 - [TenantQuota](docs/TenantQuota.md)
 - [TenantQuotaFeatureDto](docs/TenantQuotaFeatureDto.md)
 - [TenantQuotaSettings](docs/TenantQuotaSettings.md)
 - [TenantQuotaSettingsRequestsDto](docs/TenantQuotaSettingsRequestsDto.md)
 - [TenantQuotaSettingsWrapper](docs/TenantQuotaSettingsWrapper.md)
 - [TenantQuotaWrapper](docs/TenantQuotaWrapper.md)
 - [TenantRoomQuotaSettings](docs/TenantRoomQuotaSettings.md)
 - [TenantRoomQuotaSettingsWrapper](docs/TenantRoomQuotaSettingsWrapper.md)
 - [TenantStatus](docs/TenantStatus.md)
 - [TenantTrustedDomainsType](docs/TenantTrustedDomainsType.md)
 - [TenantUserInvitationSettingsDto](docs/TenantUserInvitationSettingsDto.md)
 - [TenantUserInvitationSettingsRequestDto](docs/TenantUserInvitationSettingsRequestDto.md)
 - [TenantUserInvitationSettingsWrapper](docs/TenantUserInvitationSettingsWrapper.md)
 - [TenantUserQuotaSettings](docs/TenantUserQuotaSettings.md)
 - [TenantUserQuotaSettingsWrapper](docs/TenantUserQuotaSettingsWrapper.md)
 - [TenantWalletService](docs/TenantWalletService.md)
 - [TenantWalletServiceSettings](docs/TenantWalletServiceSettings.md)
 - [TenantWalletServiceSettingsWrapper](docs/TenantWalletServiceSettingsWrapper.md)
 - [TenantWalletSettings](docs/TenantWalletSettings.md)
 - [TenantWalletSettingsWrapper](docs/TenantWalletSettingsWrapper.md)
 - [TenantWrapper](docs/TenantWrapper.md)
 - [TerminateRequestDto](docs/TerminateRequestDto.md)
 - [TfaRequestsDto](docs/TfaRequestsDto.md)
 - [TfaRequestsDtoType](docs/TfaRequestsDtoType.md)
 - [TfaSettingsArrayWrapper](docs/TfaSettingsArrayWrapper.md)
 - [TfaSettingsDto](docs/TfaSettingsDto.md)
 - [TfaValidateRequestsDto](docs/TfaValidateRequestsDto.md)
 - [ThirdPartyBackupRequestDto](docs/ThirdPartyBackupRequestDto.md)
 - [ThirdPartyParams](docs/ThirdPartyParams.md)
 - [ThirdPartyParamsArrayWrapper](docs/ThirdPartyParamsArrayWrapper.md)
 - [ThirdPartyRequestDto](docs/ThirdPartyRequestDto.md)
 - [Thumbnail](docs/Thumbnail.md)
 - [ThumbnailsDataDto](docs/ThumbnailsDataDto.md)
 - [ThumbnailsDataWrapper](docs/ThumbnailsDataWrapper.md)
 - [ThumbnailsRequest](docs/ThumbnailsRequest.md)
 - [TimezonesRequestsArrayWrapper](docs/TimezonesRequestsArrayWrapper.md)
 - [TimezonesRequestsDto](docs/TimezonesRequestsDto.md)
 - [TopUpDepositRequestDto](docs/TopUpDepositRequestDto.md)
 - [TurnOnAdminMessageSettingsRequestDto](docs/TurnOnAdminMessageSettingsRequestDto.md)
 - [UnknownWrapper](docs/UnknownWrapper.md)
 - [UpdateApiKeyRequest](docs/UpdateApiKeyRequest.md)
 - [UpdateClientRequest](docs/UpdateClientRequest.md)
 - [UpdateComment](docs/UpdateComment.md)
 - [UpdateFile](docs/UpdateFile.md)
 - [UpdateGroupRequest](docs/UpdateGroupRequest.md)
 - [UpdateMemberRequestDto](docs/UpdateMemberRequestDto.md)
 - [UpdateMembersQuotaRequestDto](docs/UpdateMembersQuotaRequestDto.md)
 - [UpdateMembersQuotaRequestDtoQuota](docs/UpdateMembersQuotaRequestDtoQuota.md)
 - [UpdateMembersRequestDto](docs/UpdateMembersRequestDto.md)
 - [UpdatePhotoMemberRequest](docs/UpdatePhotoMemberRequest.md)
 - [UpdateRoomRequest](docs/UpdateRoomRequest.md)
 - [UpdateRoomsQuotaRequestDtoInteger](docs/UpdateRoomsQuotaRequestDtoInteger.md)
 - [UpdateRoomsRoomIdsRequestDtoInteger](docs/UpdateRoomsRoomIdsRequestDtoInteger.md)
 - [UpdateWebhooksConfigRequestsDto](docs/UpdateWebhooksConfigRequestsDto.md)
 - [UploadRequestDto](docs/UploadRequestDto.md)
 - [UploadResultDto](docs/UploadResultDto.md)
 - [UploadResultWrapper](docs/UploadResultWrapper.md)
 - [UsageSpaceStatItemArrayWrapper](docs/UsageSpaceStatItemArrayWrapper.md)
 - [UsageSpaceStatItemDto](docs/UsageSpaceStatItemDto.md)
 - [UserConfig](docs/UserConfig.md)
 - [UserInfo](docs/UserInfo.md)
 - [UserInfoWrapper](docs/UserInfoWrapper.md)
 - [UserInvitation](docs/UserInvitation.md)
 - [UserInvitationRequestDto](docs/UserInvitationRequestDto.md)
 - [ValidationResult](docs/ValidationResult.md)
 - [WalletQuantityRequestDto](docs/WalletQuantityRequestDto.md)
 - [WatermarkAdditions](docs/WatermarkAdditions.md)
 - [WatermarkDto](docs/WatermarkDto.md)
 - [WatermarkOnDraw](docs/WatermarkOnDraw.md)
 - [WatermarkRequestDto](docs/WatermarkRequestDto.md)
 - [WebItemSecurityRequestsDto](docs/WebItemSecurityRequestsDto.md)
 - [WebItemsSecurityRequestsDto](docs/WebItemsSecurityRequestsDto.md)
 - [WebPluginArrayWrapper](docs/WebPluginArrayWrapper.md)
 - [WebPluginDto](docs/WebPluginDto.md)
 - [WebPluginRequests](docs/WebPluginRequests.md)
 - [WebPluginWrapper](docs/WebPluginWrapper.md)
 - [WebhookGroupStatus](docs/WebhookGroupStatus.md)
 - [WebhookRetryRequestsDto](docs/WebhookRetryRequestsDto.md)
 - [WebhookTrigger](docs/WebhookTrigger.md)
 - [WebhooksConfigDto](docs/WebhooksConfigDto.md)
 - [WebhooksConfigWithStatusArrayWrapper](docs/WebhooksConfigWithStatusArrayWrapper.md)
 - [WebhooksConfigWithStatusDto](docs/WebhooksConfigWithStatusDto.md)
 - [WebhooksConfigWrapper](docs/WebhooksConfigWrapper.md)
 - [WebhooksLogArrayWrapper](docs/WebhooksLogArrayWrapper.md)
 - [WebhooksLogDto](docs/WebhooksLogDto.md)
 - [WebhooksLogWrapper](docs/WebhooksLogWrapper.md)
 - [WhiteLabelItemArrayWrapper](docs/WhiteLabelItemArrayWrapper.md)
 - [WhiteLabelItemDto](docs/WhiteLabelItemDto.md)
 - [WhiteLabelItemPathDto](docs/WhiteLabelItemPathDto.md)
 - [WhiteLabelLogoType](docs/WhiteLabelLogoType.md)
 - [WhiteLabelRequestsDto](docs/WhiteLabelRequestsDto.md)
 - [WizardRequestsDto](docs/WizardRequestsDto.md)
 - [WizardSettings](docs/WizardSettings.md)
 - [WizardSettingsWrapper](docs/WizardSettingsWrapper.md)

</details>

