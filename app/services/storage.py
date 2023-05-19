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

from typing import List, Optional

from app.core.settings.app import AppSettings
from app.models.schemas.user import User
from app.services.base import IStorageService
from app.services.osdu_clients.storage_client import StorageServiceApiClient


class StorageService(IStorageService):

    def __init__(self, data_partition_id: str, settings: AppSettings, user: User) -> None:
        self.storage_client = StorageServiceApiClient(
            settings.service_host_storage, data_partition_id=data_partition_id, bearer_token=user.access_token,
        )

    async def get_record(self, record_id: str, version: Optional[str] = None) -> dict:
        """Get last record or versioned record if version is not none.

        :param record_id: record id
        :type record_id: str
        :param version: version, defaults to None
        :type version: Optional[str], optional
        :return: record json
        :rtype: dict
        """
        if version:
            response = await self.storage_client.get_specific_record(record_id, version)
        else:
            response = await self.storage_client.get_latest_record(record_id)
        return response

    async def get_record_versions(self, record_id: str) -> dict:
        """Get record versions.

        :param record_id: record id
        :type record_id: str
        :return: record's versions
        :rtype: dict
        """
        return await self.storage_client.get_record_versions(record_id)

    async def soft_delete_record(self, record_id: str) -> None:
        """Make record unavailable without admin rights.

        :param record_id: record id
        :type record_id: str
        """
        await self.storage_client.soft_delete_record(record_id)

    async def upsert_records(self, records: List[dict]) -> dict:
        """Upsert records.

        :param records: records
        :type records: List[dict]
        :return: upserted records ids
        :rtype: dict
        """
        return await self.storage_client.create_update_records(records)

    async def query_records(self, record_ids: list[str]) -> dict:
        """Query records by ids.

        :param record_ids: record ids
        :type record_ids: list[str]
        :return: records
        :rtype: dict
        """
        return await self.storage_client.query_records(record_ids)
