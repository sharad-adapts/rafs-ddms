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
from collections import defaultdict
from typing import Optional

from client.api.core.api_source import APIResource
from client.api_client import APIClient
from tests.integration.config import ACCEPT_HEADERS, SCHEMA_VERSION


class FractionationPaths(object):
    POST = "/fractionationtests"
    GET = "/fractionationtests/{record_id}"
    GET_VERSIONS = "/fractionationtests/{record_id}/versions"
    GET_VERSION = "/fractionationtests/{record_id}/versions/{version}"
    DELETE = "/fractionationtests/{record_id}"
    POST_DATA = "/fractionationtests/{record_id}/data"
    GET_DATA = "/fractionationtests/{record_id}/data/{dataset_id}"


class FractionationCore(APIResource, APIClient):
    """API Fractionation methods."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str):
        super().__init__(host, url_prefix, data_partition, token, FractionationPaths)

    def post_measurements(
        self,
        record_id: str,
        body: dict,
        schema_version_header: Optional[dict] = ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        **kwargs,
    ) -> dict:
        """
        :param record_id: created record_id
        :param body: measurements data
        :param schema_version_header: version of the dataset schema
        :return: created data
        """
        if schema_version_header:
            headers = defaultdict(dict, kwargs.get("headers", {}))
            headers.update({"Accept": schema_version_header})
            kwargs["headers"] = headers
        return self.post(
            path=FractionationPaths.POST_DATA.format(record_id=record_id), json=body, **kwargs,
        ).json()

    def get_measurements(
        self,
        record_id: str,
        dataset_id,
        schema_version_header: Optional[dict] = ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        **kwargs,
    ) -> dict:
        """
        :param record_id: created record id
        :param dataset_id: created dataset id
        :param schema_version_header: version of the dataset schema
        :return: measurements data
        """
        if schema_version_header:
            headers = defaultdict(dict, kwargs.get("headers", {}))
            headers.update({"Accept": schema_version_header})
            kwargs["headers"] = headers
        return self.get(
            path=FractionationPaths.GET_DATA.format(record_id=record_id, dataset_id=dataset_id), **kwargs,
        ).json()
