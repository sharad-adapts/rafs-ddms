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

from client.api.core.api_source import APIResource
from client.api_client import APIClient


class PVTModelPaths(object):
    VERSION = "/v2"
    POST = "/pvtmodel"
    GET = "/pvtmodel/{record_id}"
    GET_VERSIONS = "/pvtmodel/{record_id}/versions"
    GET_VERSION = "/pvtmodel/{record_id}/versions/{version}"
    DELETE = "/pvtmodel/{record_id}"
    GET_SOURCE_FILE = "/pvtmodel/{record_id}/source"


class PVTModelV2Core(APIResource, APIClient):
    """API PVTModel v2 methods."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str):
        super().__init__(host, PVTModelPaths.VERSION, url_prefix, data_partition, token, PVTModelPaths)
