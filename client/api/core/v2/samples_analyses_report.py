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

from client.api.core.api_source import APIResource
from client.api_client import APIClient


class SARV2Paths(object):
    VERSION = "/v2"
    POST = "/samplesanalysesreport"
    GET = "/samplesanalysesreport/{record_id}"
    GET_VERSIONS = "/samplesanalysesreport/{record_id}/versions"
    GET_VERSION = "/samplesanalysesreport/{record_id}/versions/{version}"
    DELETE = "/samplesanalysesreport/{record_id}"
    GET_SOURCE_FILE = "/samplesanalysesreport/{record_id}/source"


class SamplesAnalysesReportV2Core(APIResource, APIClient):
    """API Samples Analyses Report v2 methods."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str):
        super().__init__(host, SARV2Paths.VERSION, url_prefix, data_partition, token, SARV2Paths)
