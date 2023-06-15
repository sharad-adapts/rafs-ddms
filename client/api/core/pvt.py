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

from requests import Response

from client.api.core.api_source import APIResource
from client.api_client import APIClient


class PVTPaths(object):
    POST = "/pvtreports"
    GET = "/pvtreports/{record_id}"
    GET_VERSIONS = "/pvtreports/{record_id}/versions"
    GET_VERSION = "/pvtreports/{record_id}/versions/{version}"
    DELETE = "/pvtreports/{record_id}"
    GET_FILE_DOWNLOAD = "/pvtreports/{record_id}/source"


class PVTCore(APIResource, APIClient):
    """API PVT methods."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str):
        super().__init__(host, url_prefix, data_partition, token, PVTPaths)

    def get_file(self, record_id: str, **kwargs) -> Response:
        return self.get(path=PVTPaths.GET_FILE_DOWNLOAD.format(record_id=record_id), **kwargs)
