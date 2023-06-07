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


class CoringCorePaths(object):
    POST_CORING = "/coringreports"
    GET_CORING = "/coringreports/{record_id}"
    GET_VERSIONS = "/coringreports/{record_id}/versions"
    GET_VERSION = "/coringreports/{record_id}/versions/{version}"
    DELETE_CORING = "/coringreports/{record_id}"


class CoringCore(APIClient):
    """API Coring methods."""

    def post_coring_data(self, body: list, **kwargs) -> dict:
        """
        :param body: coring data
        :return: created coring record
        """
        return self.post(path=CoringCorePaths.POST_CORING, json=body, **kwargs).json()

    def get_coring_data(
        self, record_id: str, version: Optional[str] = None, **kwargs,
    ) -> dict:
        """
        :param record_id: coring record id
        :param version: coring version
        :return: coring data
        """
        params_dict = {"version": version}
        return self.get(
            path=CoringCorePaths.GET_CORING.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        return self.get(
            path=CoringCorePaths.GET_VERSIONS.format(record_id=record_id), **kwargs,
        ).json()

    def get_version_of_the_record(self, record_id: str, version: int, **kwargs) -> dict:
        return self.get(
            path=CoringCorePaths.GET_VERSION.format(record_id=record_id, version=version), **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        self.delete(
            path=CoringCorePaths.DELETE_CORING.format(record_id=record_id), **kwargs,
        )
