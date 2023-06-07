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

from requests import Response

from client.api_client import APIClient


class PVTPaths(object):
    POST = "/pvtreports"
    GET = "/pvtreports/{record_id}"
    GET_VERSIONS = "/pvtreports/{record_id}/versions"
    GET_VERSION = "/pvtreports/{record_id}/versions/{version}"
    DELETE = "/pvtreports/{record_id}"
    GET_FILE_DOWNLOAD = "/pvtreports/{record_id}/source"


class PVTCore(APIClient):
    """API PVT methods."""

    def post_pvt_data(self, body: list, **kwargs) -> dict:
        """
        :param body: pvt data
        :return: created pvt record
        """
        return self.post(path=PVTPaths.POST, json=body, **kwargs).json()

    def get_pvt_data(
        self, record_id: str, version: Optional[str] = None, **kwargs,
    ) -> dict:
        """
        :param record_id: pvt record id
        :param version: pvt version
        :return: pvt data
        """
        params_dict = {"version": version}
        return self.get(
            path=PVTPaths.GET.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        return self.get(
            path=PVTPaths.GET_VERSIONS.format(record_id=record_id), **kwargs,
        ).json()

    def get_version_of_the_record(self, record_id: str, version: int, **kwargs) -> dict:
        return self.get(
            path=PVTPaths.GET_VERSION.format(record_id=record_id, version=version), **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        self.delete(
            path=PVTPaths.DELETE.format(record_id=record_id), **kwargs,
        )

    def get_pvt_file(self, record_id: str, **kwargs) -> Response:
        return self.get(path=PVTPaths.GET_FILE_DOWNLOAD.format(record_id=record_id), **kwargs)
