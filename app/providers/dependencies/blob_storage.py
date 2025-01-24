#  Copyright 2024 ExxonMobil Technology and Engineering Company
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings

from app.core.settings.app import AppSettings
from app.resources.mime_types import MimeType


@dataclass
class BlobMetadata:
    analysis_family: str
    analysis_type: str
    version: str
    uuid: str
    content_type: MimeType
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not all([self.analysis_family, self.analysis_type, self.version, self.uuid, self.content_type]):
            raise ValueError(
                "analysis_famuly, analysis_type, version, uuid, and content_type must be non-empty strings.",
            )

    @property
    def object_name(self) -> str:
        return f"{self.analysis_family}/{self.analysis_type}/{self.version}/{self.uuid}"

    @property
    def full_analysis_type(self) -> str:
        return f"{self.analysis_family}/{self.analysis_type}/{self.version}"


@dataclass
class Blob:
    blob_data: bytes
    blob_metadata: BlobMetadata


@dataclass
class StoragePartitionInfo:
    data_partition_id: str
    storage_account_info: Dict[str, Any]


class IBlobStorage(ABC):
    """Abstract class for cloud storage backends."""

    @abstractmethod
    async def create_blob(
        self,
        blob: Blob,
    ) -> BlobMetadata:
        """Create the blob in the storage backend.

        :param blob: the blob to upload
        :type blob: Blob
        :return: the uploaded blob metadata
        :rtype: BlobMetadata
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_blob(
        self,
        blob_metadata: BlobMetadata,
    ) -> bool:
        """Deletes the blob with given metadata.

        :param blob_metadata: the blob metadata
        :type blob_metadata: BlobMetadata
        :return: True if success
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    async def update_blob(
        self,
        blob: Blob,
    ) -> BlobMetadata:
        """Updates blob with new content.

        :param blob: the blob to upload
        :type blob: Blob
        :return: the uploaded blob metadata
        :rtype: BlobMetadata
        """
        raise NotImplementedError

    @abstractmethod
    async def get_blob(
        self,
        blob_metadata: BlobMetadata,
    ) -> Blob:
        """Gets the blob with given metadata.

        :param blob_metadata: the blob metadata
        :type blob_metadata: BlobMetadata
        :return: the blob with content
        :rtype: Blob
        """
        raise NotImplementedError

    @abstractmethod
    async def list_blobs(
        self,
        subpath: str,
    ) -> List[str]:
        """List the blobs given a subpath.

        :param subpath: subpatht of the , e.g.,
            samplesanalysis/nmr/1.0.0/ or pvt/eos/1.0.0
        :type analysis_type: str
        :return: list of blobs
        :rtype: List[str]
        """
        raise NotImplementedError


async def get_blob_storage(
    data_partition_id: str,
    settings: AppSettings,
    cloud_provider_config: Optional[BaseSettings],
    **kwargs,
) -> IBlobStorage:
    match settings.cloud_provider:
        case "azure":
            from app.providers.dependencies.az.blob_storage import (
                AzureBlobStorage,
            )
            from app.providers.dependencies.az.storage_account_info import (
                AzureStorageAccountInfo,
            )
            async with AzureStorageAccountInfo(
                data_partition_id, settings, cloud_provider_config,
            ) as azure_storage_account_info:
                account_info = await azure_storage_account_info.get_info()
                return AzureBlobStorage(StoragePartitionInfo(data_partition_id, account_info))
        case _:
            raise NotImplementedError()
