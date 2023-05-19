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

from abc import ABC, abstractmethod
from typing import List, Optional


class IStorageService(ABC):

    @abstractmethod
    async def get_record(self, record_id: str, version: Optional[str] = None) -> dict:
        """Get record.

        :param record_id: record id
        :type record_id: str
        :param version: version, defaults to None
        :type version: Optional[str], optional
        :raises NotImplementedError: method is supposed to be implemented
        :return: record
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_record_versions(self, record_id: str) -> dict:
        """Get record versions.

        :param record_id: record id
        :type record_id: str
        :raises NotImplementedError: method is supposed to be implemented
        :return: record versions
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    async def upsert_records(self, records: List[dict]) -> dict:
        """Upsert records.

        :param records: records
        :type records: List[dict]
        :raises NotImplementedError: method is supposed to be implemented
        :return: upserted records ids
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    async def soft_delete_record(self, record_id: str) -> None:
        """Make record unavailable without admin rights.

        :param record_id: record id
        :type record_id: str
        :raises NotImplementedError: method is supposed to be implemented
        """
        raise NotImplementedError()

    @abstractmethod
    async def query_records(self, record_ids: list[str]) -> dict:
        """Query records.

        :param record_ids: record ids
        :type record_ids: list[str]
        :raises NotImplementedError: method is supposed to be implemented
        :return: records
        :rtype: dict
        """
        raise NotImplementedError()


class IDatasetService(ABC):

    @abstractmethod
    async def download_file(self, dataset_id: str) -> Optional[bytes]:
        """Download file.

        :param dataset_id: dataset id
        :type dataset_id: str
        :raises NotImplementedError: method is supposed to be implemented
        :return: file content
        :rtype: Optional[bytes]
        """
        raise NotImplementedError()

    @abstractmethod
    async def upload_file(self, blob_file: bytes, dataset_id: str, parent_record: dict) -> str:
        """Upload file.

        :param blob_file: blob file
        :type blob_file: bytes
        :param dataset_id: dataset id
        :type dataset_id: str
        :param parent_record: parent record
        :type parent_record: dict
        :raises NotImplementedError: method is supposed to be implemented
        :return: stored dataset id and version
        :rtype: str
        """
        raise NotImplementedError()


class ISearchService(ABC):

    @abstractmethod
    async def find_records(self, kind: Optional[str], optional_search_params: Optional[dict] = None) -> List[dict]:
        """Find records.

        :param kind: kind
        :type kind: Optional[str]
        :param optional_search_params: optional params, defaults to None
        :type optional_search_params: Optional[dict], optional
        :raises NotImplementedError: method is supposed to be implemented
        :return: records
        :rtype: List[dict]
        """
        raise NotImplementedError()
