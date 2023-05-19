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


class RockSampleCorePaths(object):
    COMMON_PART = f"/api/rafs-ddms/{API_VERSION}"
    POST_RS = f"{COMMON_PART}/rocksamples"
    GET_RS = f"{COMMON_PART}/rocksamples/{{record_id}}"
    GET_VERSIONS = f"{COMMON_PART}/rocksamples/{{record_id}}/versions"
    GET_VERSION = f"{COMMON_PART}/rocksamples/{{record_id}}/versions/{{version}}"
    DELETE_RS = f"{COMMON_PART}/rocksamples/{{record_id}}"


class RockSampleCore(APIClient):
    """API Rock Sample methods."""

    def post_rs_data(self, body: list, **kwargs) -> dict:
        """
        :param body: rock sample data
        :return: created rock sample
        """
        return self.post(path=RockSampleCorePaths.POST_RS, json=body, **kwargs).json()

    def get_rs_data(
        self, record_id: str, version: Optional[str] = None, **kwargs,
    ) -> dict:
        """
        :param record_id: rock sample record id
        :param version: rock sample version
        :return: rock sample data
        """
        params_dict = {"version": version}
        return self.get(
            path=RockSampleCorePaths.GET_RS.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        return self.get(
            path=RockSampleCorePaths.GET_VERSIONS.format(record_id=record_id), **kwargs,
        ).json()

    def get_version_of_the_record(self, record_id: str, version: int, **kwargs) -> dict:
        return self.get(
            path=RockSampleCorePaths.GET_VERSION.format(record_id=record_id, version=version),
            **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        self.delete(path=RockSampleCorePaths.DELETE_RS.format(record_id=record_id), **kwargs)
