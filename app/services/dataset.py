#  Copyright 2023 ExxonMobil Technology and Engineering Company
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

import sys
from typing import Optional

from app.core.settings.app import AppSettings
from app.models.schemas.user import User
from app.providers.dependencies.blob_loader import get_blob_loader
from app.services.base import IDatasetService
from app.services.osdu_clients.dataset_client import DatasetServiceApiClient
from app.services.utils.dataset import create_default_dataset_record


class DatasetService(IDatasetService):

    def __init__(self, data_partition_id: str, settings: AppSettings, user: User) -> None:
        self.schema_authority = settings.schema_authority
        self.dataset_client = DatasetServiceApiClient(
            settings.service_host_dataset, data_partition_id=data_partition_id, bearer_token=user.access_token,
        )
        self.blob_loader = get_blob_loader(settings)

    async def download_file(self, dataset_id: str) -> Optional[bytes]:
        """Download file.

        :param dataset_id: dataset id
        :type dataset_id: str
        :return: file content
        :rtype: Optional[bytes]
        """
        retrieval_instruction = await self.dataset_client.get_retrieval_instructions(dataset_id)
        if retrieval_instruction.get("datasets"):
            signed_url = retrieval_instruction["datasets"][0]["retrievalProperties"]["signedUrl"]
            return await self.blob_loader.download_blob(signed_url)

    async def upload_file(
        self, blob_file: bytes, dataset_id: str, parent_record: dict,
    ) -> str:
        """Upload file.

        :param blob_file: blob file
        :type blob_file: bytes
        :param dataset_id: dataset id
        :type dataset_id: str
        :param parent_record: parent record
        :type parent_record: dict
        :return: stored dataset id and version
        :rtype: str
        """
        storage_instruction = await self.dataset_client.storage_instructions(
            kind_subtype="dataset--File.Generic",
        )
        signed_url = storage_instruction["storageLocation"]["signedUrl"]
        file_source = storage_instruction["storageLocation"]["fileSource"]

        await self.blob_loader.upload_blob(signed_url, blob_file)

        record_list = [
            create_default_dataset_record(
                dataset_id,
                file_source,
                str(sys.getsizeof(blob_file)),
                parent_record,
                self.schema_authority,
            ),
        ]
        registered_dataset = await self.dataset_client.create_or_update_dataset_registry(dataset_registries=record_list)

        stored_dataset = registered_dataset["datasetRegistries"][0]
        return f"{stored_dataset['id']}:{stored_dataset['version']}"
