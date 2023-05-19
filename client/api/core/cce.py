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

from typing import Optional

from client.api_client import APIClient
from tests.test_api.api_version import API_VERSION


class CCEPaths(object):
    COMMON_PART = f"/api/rafs-ddms/{API_VERSION}"
    POST = f"{COMMON_PART}/ccereports"
    GET = f"{COMMON_PART}/ccereports/{{record_id}}"
    GET_VERSIONS = f"{COMMON_PART}/ccereports/{{record_id}}/versions"
    GET_VERSION = f"{COMMON_PART}/ccereports/{{record_id}}/versions/{{version}}"
    DELETE = f"{COMMON_PART}/ccereports/{{record_id}}"
    GET_FILE_DOWNLOAD = f"{COMMON_PART}/ccereports/{{record_id}}/source"
    POST_DATA = f"{COMMON_PART}/ccereports/{{record_id}}/data"
    GET_DATA = f"{COMMON_PART}/ccereports/{{record_id}}/data/{{cce_dataset_id}}"


class CCECore(APIClient):
    """API CCE methods."""

    def post_cce_data(self, body: list, **kwargs) -> dict:
        """
        :param body: cce data
        :return: created cce record
        """
        return self.post(path=CCEPaths.POST, json=body, **kwargs).json()

    def get_cce_data(
        self, record_id: str, version: Optional[str] = None, **kwargs,
    ) -> dict:
        """
        :param record_id: cce record id
        :param version: cce version
        :return: cce data
        """
        params_dict = {"version": version}
        return self.get(
            path=CCEPaths.GET.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        return self.get(
            path=CCEPaths.GET_VERSIONS.format(record_id=record_id), **kwargs,
        ).json()

    def get_version_of_the_record(self, record_id: str, version: int, **kwargs) -> dict:
        return self.get(
            path=CCEPaths.GET_VERSION.format(record_id=record_id, version=version), **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        self.delete(
            path=CCEPaths.DELETE.format(record_id=record_id), **kwargs,
        )

    def post_measurements(self, record_id: str, body: dict, **kwargs) -> dict:
        """
        :param record_id: created record_id
        :param body: cce measurements data
        :return: created cce data
        """
        return self.post(
            path=CCEPaths.POST_DATA.format(record_id=record_id), json=body, **kwargs,
        ).json()

    def get_measurements(self, record_id: str, dataset_id, **kwargs) -> dict:
        """
        :param record_id: created record id
        :param dataset_id: created dataset id
        :param kwargs:
        :return: cce measurements data
        """
        return self.get(
            path=CCEPaths.GET_DATA.format(record_id=record_id, cce_dataset_id=dataset_id), **kwargs,
        ).json()
