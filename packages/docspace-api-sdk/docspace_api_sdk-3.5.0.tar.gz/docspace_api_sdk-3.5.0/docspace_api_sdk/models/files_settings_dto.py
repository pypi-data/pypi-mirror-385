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
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from docspace_api_sdk.models.auto_clean_up_data import AutoCleanUpData
from docspace_api_sdk.models.files_settings_dto_internal_formats import FilesSettingsDtoInternalFormats
from docspace_api_sdk.models.order_by import OrderBy
from typing import Optional, Set
from typing_extensions import Self

class FilesSettingsDto(BaseModel):
    """
    The file settings parameters.
    """ # noqa: E501
    exts_image_previewed: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the viewed images.", alias="extsImagePreviewed")
    exts_media_previewed: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the viewed media files.", alias="extsMediaPreviewed")
    exts_web_previewed: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the viewed files.", alias="extsWebPreviewed")
    exts_web_edited: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the edited files.", alias="extsWebEdited")
    exts_web_encrypt: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the encrypted files.", alias="extsWebEncrypt")
    exts_web_reviewed: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the reviewed files.", alias="extsWebReviewed")
    exts_web_custom_filter_editing: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the custom filter files.", alias="extsWebCustomFilterEditing")
    exts_web_restricted_editing: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the files that are restricted for editing.", alias="extsWebRestrictedEditing")
    exts_web_commented: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the commented files.", alias="extsWebCommented")
    exts_web_template: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the template files.", alias="extsWebTemplate")
    exts_must_convert: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the files that must be converted.", alias="extsMustConvert")
    exts_convertible: Optional[Dict[str, Optional[List[StrictStr]]]] = Field(default=None, description="The list of the convertible extensions.", alias="extsConvertible")
    exts_uploadable: Optional[List[StrictStr]] = Field(default=None, description="The list of the uploadable extensions.", alias="extsUploadable")
    exts_archive: Optional[List[StrictStr]] = Field(default=None, description="The list of extensions of the archive files.", alias="extsArchive")
    exts_video: Optional[List[StrictStr]] = Field(default=None, description="The list of the video extensions.", alias="extsVideo")
    exts_audio: Optional[List[StrictStr]] = Field(default=None, description="The list of the audio extensions.", alias="extsAudio")
    exts_image: Optional[List[StrictStr]] = Field(default=None, description="The list of the image extensions.", alias="extsImage")
    exts_spreadsheet: Optional[List[StrictStr]] = Field(default=None, description="The list of the spreadsheet extensions.", alias="extsSpreadsheet")
    exts_presentation: Optional[List[StrictStr]] = Field(default=None, description="The list of the presentation extensions.", alias="extsPresentation")
    exts_document: Optional[List[StrictStr]] = Field(default=None, description="The list of the text document extensions.", alias="extsDocument")
    exts_diagram: Optional[List[StrictStr]] = Field(default=None, description="The list of the diagram extensions.", alias="extsDiagram")
    internal_formats: Optional[FilesSettingsDtoInternalFormats] = Field(default=None, alias="internalFormats")
    master_form_extension: Optional[StrictStr] = Field(default=None, description="The master form extension.", alias="masterFormExtension")
    param_version: Optional[StrictStr] = Field(default=None, description="The URL parameter which specifies the file version.", alias="paramVersion")
    param_out_type: Optional[StrictStr] = Field(default=None, description="The URL parameter which specifies the output type of the converted file.", alias="paramOutType")
    file_download_url_string: Optional[StrictStr] = Field(default=None, description="The URL to download a file.", alias="fileDownloadUrlString")
    file_web_viewer_url_string: Optional[StrictStr] = Field(default=None, description="The URL to the file web viewer.", alias="fileWebViewerUrlString")
    file_web_viewer_external_url_string: Optional[StrictStr] = Field(default=None, description="The external URL to the file web viewer.", alias="fileWebViewerExternalUrlString")
    file_web_editor_url_string: Optional[StrictStr] = Field(default=None, description="The URL to the file web editor.", alias="fileWebEditorUrlString")
    file_web_editor_external_url_string: Optional[StrictStr] = Field(default=None, description="The external URL to the file web editor.", alias="fileWebEditorExternalUrlString")
    file_redirect_preview_url_string: Optional[StrictStr] = Field(default=None, description="The redirect URL to the file viewer.", alias="fileRedirectPreviewUrlString")
    file_thumbnail_url_string: Optional[StrictStr] = Field(default=None, description="The URL to the file thumbnail.", alias="fileThumbnailUrlString")
    confirm_delete: Optional[StrictBool] = Field(default=None, description="Specifies whether to confirm the file deletion or not.", alias="confirmDelete")
    enable_third_party: Optional[StrictBool] = Field(default=None, description="Specifies whether to allow users to connect the third-party storages.", alias="enableThirdParty")
    external_share: Optional[StrictBool] = Field(default=None, description="Specifies whether to enable sharing external links to the files.", alias="externalShare")
    external_share_social_media: Optional[StrictBool] = Field(default=None, description="Specifies whether to enable sharing files on social media.", alias="externalShareSocialMedia")
    store_original_files: Optional[StrictBool] = Field(default=None, description="Specifies whether to enable storing original files.", alias="storeOriginalFiles")
    keep_new_file_name: Optional[StrictBool] = Field(default=None, description="Specifies whether to keep the new file name.", alias="keepNewFileName")
    display_file_extension: Optional[StrictBool] = Field(default=None, description="Specifies whether to display the file extension.", alias="displayFileExtension")
    convert_notify: Optional[StrictBool] = Field(default=None, description="Specifies whether to display the conversion notification.", alias="convertNotify")
    hide_confirm_cancel_operation: Optional[StrictBool] = Field(default=None, description="Specifies whether to hide the confirmation dialog for the cancel operation.", alias="hideConfirmCancelOperation")
    hide_confirm_convert_save: Optional[StrictBool] = Field(default=None, description="Specifies whether to hide the confirmation dialog  for saving the file copy in the original format when converting a file.", alias="hideConfirmConvertSave")
    hide_confirm_convert_open: Optional[StrictBool] = Field(default=None, description="Specifies whether to hide the confirmation dialog  for opening the conversion result.", alias="hideConfirmConvertOpen")
    hide_confirm_room_lifetime: Optional[StrictBool] = Field(default=None, description="Specifies whether to hide the confirmation dialog about the file lifetime in the room.", alias="hideConfirmRoomLifetime")
    default_order: Optional[OrderBy] = Field(default=None, alias="defaultOrder")
    forcesave: Optional[StrictBool] = Field(default=None, description="Specifies whether to forcesave the files or not.")
    store_forcesave: Optional[StrictBool] = Field(default=None, description="Specifies whether to store the forcesaved file versions or not.", alias="storeForcesave")
    recent_section: Optional[StrictBool] = Field(default=None, description="Specifies if the Recent section is displayed or not.", alias="recentSection")
    favorites_section: Optional[StrictBool] = Field(default=None, description="Specifies if the Favorites section is displayed or not.", alias="favoritesSection")
    templates_section: Optional[StrictBool] = Field(default=None, description="Specifies if the Templates section is displayed or not.", alias="templatesSection")
    download_tar_gz: Optional[StrictBool] = Field(default=None, description="Specifies whether to download the .tar.gz files or not.", alias="downloadTarGz")
    automatically_clean_up: Optional[AutoCleanUpData] = Field(default=None, alias="automaticallyCleanUp")
    can_search_by_content: Optional[StrictBool] = Field(default=None, description="Specifies whether the file can be searched by its content or not.", alias="canSearchByContent")
    default_sharing_access_rights: Optional[List[StrictInt]] = Field(default=None, description="The default access rights in sharing settings.", alias="defaultSharingAccessRights")
    max_upload_thread_count: Optional[StrictInt] = Field(default=None, description="The maximum number of upload threads.", alias="maxUploadThreadCount")
    chunk_upload_size: Optional[StrictInt] = Field(default=None, description="The size of a large file that is uploaded in chunks.", alias="chunkUploadSize")
    open_editor_in_same_tab: Optional[StrictBool] = Field(default=None, description="Specifies whether to open the editor in the same tab or not.", alias="openEditorInSameTab")
    __properties: ClassVar[List[str]] = ["extsImagePreviewed", "extsMediaPreviewed", "extsWebPreviewed", "extsWebEdited", "extsWebEncrypt", "extsWebReviewed", "extsWebCustomFilterEditing", "extsWebRestrictedEditing", "extsWebCommented", "extsWebTemplate", "extsMustConvert", "extsConvertible", "extsUploadable", "extsArchive", "extsVideo", "extsAudio", "extsImage", "extsSpreadsheet", "extsPresentation", "extsDocument", "extsDiagram", "internalFormats", "masterFormExtension", "paramVersion", "paramOutType", "fileDownloadUrlString", "fileWebViewerUrlString", "fileWebViewerExternalUrlString", "fileWebEditorUrlString", "fileWebEditorExternalUrlString", "fileRedirectPreviewUrlString", "fileThumbnailUrlString", "confirmDelete", "enableThirdParty", "externalShare", "externalShareSocialMedia", "storeOriginalFiles", "keepNewFileName", "displayFileExtension", "convertNotify", "hideConfirmCancelOperation", "hideConfirmConvertSave", "hideConfirmConvertOpen", "hideConfirmRoomLifetime", "defaultOrder", "forcesave", "storeForcesave", "recentSection", "favoritesSection", "templatesSection", "downloadTarGz", "automaticallyCleanUp", "canSearchByContent", "defaultSharingAccessRights", "maxUploadThreadCount", "chunkUploadSize", "openEditorInSameTab"]

    @field_validator('default_sharing_access_rights')
    def default_sharing_access_rights_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
                raise ValueError("each list item must be one of (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of FilesSettingsDto from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of internal_formats
        if self.internal_formats:
            _dict['internalFormats'] = self.internal_formats.to_dict()
        # override the default output from pydantic by calling `to_dict()` of default_order
        if self.default_order:
            _dict['defaultOrder'] = self.default_order.to_dict()
        # override the default output from pydantic by calling `to_dict()` of automatically_clean_up
        if self.automatically_clean_up:
            _dict['automaticallyCleanUp'] = self.automatically_clean_up.to_dict()
        # set to None if exts_image_previewed (nullable) is None
        # and model_fields_set contains the field
        if self.exts_image_previewed is None and "exts_image_previewed" in self.model_fields_set:
            _dict['extsImagePreviewed'] = None

        # set to None if exts_media_previewed (nullable) is None
        # and model_fields_set contains the field
        if self.exts_media_previewed is None and "exts_media_previewed" in self.model_fields_set:
            _dict['extsMediaPreviewed'] = None

        # set to None if exts_web_previewed (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_previewed is None and "exts_web_previewed" in self.model_fields_set:
            _dict['extsWebPreviewed'] = None

        # set to None if exts_web_edited (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_edited is None and "exts_web_edited" in self.model_fields_set:
            _dict['extsWebEdited'] = None

        # set to None if exts_web_encrypt (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_encrypt is None and "exts_web_encrypt" in self.model_fields_set:
            _dict['extsWebEncrypt'] = None

        # set to None if exts_web_reviewed (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_reviewed is None and "exts_web_reviewed" in self.model_fields_set:
            _dict['extsWebReviewed'] = None

        # set to None if exts_web_custom_filter_editing (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_custom_filter_editing is None and "exts_web_custom_filter_editing" in self.model_fields_set:
            _dict['extsWebCustomFilterEditing'] = None

        # set to None if exts_web_restricted_editing (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_restricted_editing is None and "exts_web_restricted_editing" in self.model_fields_set:
            _dict['extsWebRestrictedEditing'] = None

        # set to None if exts_web_commented (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_commented is None and "exts_web_commented" in self.model_fields_set:
            _dict['extsWebCommented'] = None

        # set to None if exts_web_template (nullable) is None
        # and model_fields_set contains the field
        if self.exts_web_template is None and "exts_web_template" in self.model_fields_set:
            _dict['extsWebTemplate'] = None

        # set to None if exts_must_convert (nullable) is None
        # and model_fields_set contains the field
        if self.exts_must_convert is None and "exts_must_convert" in self.model_fields_set:
            _dict['extsMustConvert'] = None

        # set to None if exts_convertible (nullable) is None
        # and model_fields_set contains the field
        if self.exts_convertible is None and "exts_convertible" in self.model_fields_set:
            _dict['extsConvertible'] = None

        # set to None if exts_uploadable (nullable) is None
        # and model_fields_set contains the field
        if self.exts_uploadable is None and "exts_uploadable" in self.model_fields_set:
            _dict['extsUploadable'] = None

        # set to None if exts_archive (nullable) is None
        # and model_fields_set contains the field
        if self.exts_archive is None and "exts_archive" in self.model_fields_set:
            _dict['extsArchive'] = None

        # set to None if exts_video (nullable) is None
        # and model_fields_set contains the field
        if self.exts_video is None and "exts_video" in self.model_fields_set:
            _dict['extsVideo'] = None

        # set to None if exts_audio (nullable) is None
        # and model_fields_set contains the field
        if self.exts_audio is None and "exts_audio" in self.model_fields_set:
            _dict['extsAudio'] = None

        # set to None if exts_image (nullable) is None
        # and model_fields_set contains the field
        if self.exts_image is None and "exts_image" in self.model_fields_set:
            _dict['extsImage'] = None

        # set to None if exts_spreadsheet (nullable) is None
        # and model_fields_set contains the field
        if self.exts_spreadsheet is None and "exts_spreadsheet" in self.model_fields_set:
            _dict['extsSpreadsheet'] = None

        # set to None if exts_presentation (nullable) is None
        # and model_fields_set contains the field
        if self.exts_presentation is None and "exts_presentation" in self.model_fields_set:
            _dict['extsPresentation'] = None

        # set to None if exts_document (nullable) is None
        # and model_fields_set contains the field
        if self.exts_document is None and "exts_document" in self.model_fields_set:
            _dict['extsDocument'] = None

        # set to None if exts_diagram (nullable) is None
        # and model_fields_set contains the field
        if self.exts_diagram is None and "exts_diagram" in self.model_fields_set:
            _dict['extsDiagram'] = None

        # set to None if internal_formats (nullable) is None
        # and model_fields_set contains the field
        if self.internal_formats is None and "internal_formats" in self.model_fields_set:
            _dict['internalFormats'] = None

        # set to None if master_form_extension (nullable) is None
        # and model_fields_set contains the field
        if self.master_form_extension is None and "master_form_extension" in self.model_fields_set:
            _dict['masterFormExtension'] = None

        # set to None if param_version (nullable) is None
        # and model_fields_set contains the field
        if self.param_version is None and "param_version" in self.model_fields_set:
            _dict['paramVersion'] = None

        # set to None if param_out_type (nullable) is None
        # and model_fields_set contains the field
        if self.param_out_type is None and "param_out_type" in self.model_fields_set:
            _dict['paramOutType'] = None

        # set to None if file_download_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_download_url_string is None and "file_download_url_string" in self.model_fields_set:
            _dict['fileDownloadUrlString'] = None

        # set to None if file_web_viewer_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_web_viewer_url_string is None and "file_web_viewer_url_string" in self.model_fields_set:
            _dict['fileWebViewerUrlString'] = None

        # set to None if file_web_viewer_external_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_web_viewer_external_url_string is None and "file_web_viewer_external_url_string" in self.model_fields_set:
            _dict['fileWebViewerExternalUrlString'] = None

        # set to None if file_web_editor_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_web_editor_url_string is None and "file_web_editor_url_string" in self.model_fields_set:
            _dict['fileWebEditorUrlString'] = None

        # set to None if file_web_editor_external_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_web_editor_external_url_string is None and "file_web_editor_external_url_string" in self.model_fields_set:
            _dict['fileWebEditorExternalUrlString'] = None

        # set to None if file_redirect_preview_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_redirect_preview_url_string is None and "file_redirect_preview_url_string" in self.model_fields_set:
            _dict['fileRedirectPreviewUrlString'] = None

        # set to None if file_thumbnail_url_string (nullable) is None
        # and model_fields_set contains the field
        if self.file_thumbnail_url_string is None and "file_thumbnail_url_string" in self.model_fields_set:
            _dict['fileThumbnailUrlString'] = None

        # set to None if default_sharing_access_rights (nullable) is None
        # and model_fields_set contains the field
        if self.default_sharing_access_rights is None and "default_sharing_access_rights" in self.model_fields_set:
            _dict['defaultSharingAccessRights'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FilesSettingsDto from a dict"""
        if obj is None:
            return None


        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "extsImagePreviewed": obj.get("extsImagePreviewed"),
            "extsMediaPreviewed": obj.get("extsMediaPreviewed"),
            "extsWebPreviewed": obj.get("extsWebPreviewed"),
            "extsWebEdited": obj.get("extsWebEdited"),
            "extsWebEncrypt": obj.get("extsWebEncrypt"),
            "extsWebReviewed": obj.get("extsWebReviewed"),
            "extsWebCustomFilterEditing": obj.get("extsWebCustomFilterEditing"),
            "extsWebRestrictedEditing": obj.get("extsWebRestrictedEditing"),
            "extsWebCommented": obj.get("extsWebCommented"),
            "extsWebTemplate": obj.get("extsWebTemplate"),
            "extsMustConvert": obj.get("extsMustConvert"),
            "extsConvertible": obj.get("extsConvertible"),
            "extsUploadable": obj.get("extsUploadable"),
            "extsArchive": obj.get("extsArchive"),
            "extsVideo": obj.get("extsVideo"),
            "extsAudio": obj.get("extsAudio"),
            "extsImage": obj.get("extsImage"),
            "extsSpreadsheet": obj.get("extsSpreadsheet"),
            "extsPresentation": obj.get("extsPresentation"),
            "extsDocument": obj.get("extsDocument"),
            "extsDiagram": obj.get("extsDiagram"),
            "internalFormats": FilesSettingsDtoInternalFormats.from_dict(obj["internalFormats"]) if obj.get("internalFormats") is not None else None,
            "masterFormExtension": obj.get("masterFormExtension"),
            "paramVersion": obj.get("paramVersion"),
            "paramOutType": obj.get("paramOutType"),
            "fileDownloadUrlString": obj.get("fileDownloadUrlString"),
            "fileWebViewerUrlString": obj.get("fileWebViewerUrlString"),
            "fileWebViewerExternalUrlString": obj.get("fileWebViewerExternalUrlString"),
            "fileWebEditorUrlString": obj.get("fileWebEditorUrlString"),
            "fileWebEditorExternalUrlString": obj.get("fileWebEditorExternalUrlString"),
            "fileRedirectPreviewUrlString": obj.get("fileRedirectPreviewUrlString"),
            "fileThumbnailUrlString": obj.get("fileThumbnailUrlString"),
            "confirmDelete": obj.get("confirmDelete"),
            "enableThirdParty": obj.get("enableThirdParty"),
            "externalShare": obj.get("externalShare"),
            "externalShareSocialMedia": obj.get("externalShareSocialMedia"),
            "storeOriginalFiles": obj.get("storeOriginalFiles"),
            "keepNewFileName": obj.get("keepNewFileName"),
            "displayFileExtension": obj.get("displayFileExtension"),
            "convertNotify": obj.get("convertNotify"),
            "hideConfirmCancelOperation": obj.get("hideConfirmCancelOperation"),
            "hideConfirmConvertSave": obj.get("hideConfirmConvertSave"),
            "hideConfirmConvertOpen": obj.get("hideConfirmConvertOpen"),
            "hideConfirmRoomLifetime": obj.get("hideConfirmRoomLifetime"),
            "defaultOrder": OrderBy.from_dict(obj["defaultOrder"]) if obj.get("defaultOrder") is not None else None,
            "forcesave": obj.get("forcesave"),
            "storeForcesave": obj.get("storeForcesave"),
            "recentSection": obj.get("recentSection"),
            "favoritesSection": obj.get("favoritesSection"),
            "templatesSection": obj.get("templatesSection"),
            "downloadTarGz": obj.get("downloadTarGz"),
            "automaticallyCleanUp": AutoCleanUpData.from_dict(obj["automaticallyCleanUp"]) if obj.get("automaticallyCleanUp") is not None else None,
            "canSearchByContent": obj.get("canSearchByContent"),
            "defaultSharingAccessRights": obj.get("defaultSharingAccessRights"),
            "maxUploadThreadCount": obj.get("maxUploadThreadCount"),
            "chunkUploadSize": obj.get("chunkUploadSize"),
            "openEditorInSameTab": obj.get("openEditorInSameTab")
        })
        return _obj


