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
from typing import Optional, Union

from requests import Response

from client.api.core.api_source import APIResource
from client.api_client import APIClient
from tests.integration.config import ACCEPT_HEADERS, SCHEMA_VERSION


class RSACorePaths(object):
    POST = "/rocksampleanalyses"
    GET = "/rocksampleanalyses/{record_id}"
    POST_DATA = "/rocksampleanalyses/{record_id}/rca/data"
    GET_DATA = "/rocksampleanalyses/{record_id}/rca/data/{dataset_id}"
    GET_VERSIONS = "/rocksampleanalyses/{record_id}/versions"
    GET_VERSION = "/rocksampleanalyses/{record_id}/versions/{version}"
    DELETE = "/rocksampleanalyses/{record_id}"
    GET_FILE_DOWNLOAD = "/rocksampleanalyses/{record_id}/rca/source"


class RSACore(APIResource, APIClient):
    """API RSA methods."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str):
        super().__init__(host, url_prefix, data_partition, token, RSACorePaths)

    def post_measurements(
        self,
        record_id: str,
        body: dict,
        schema_version_header: Optional[dict] = ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        **kwargs,
    ) -> dict:
        """
        :param record_id: record_id from post_rsa
        :param body: rca data
        :param schema_version_header: version of the dataset schema
        :return: created rca data
        """
        body_kwarg = (
            {"data": body}
            if isinstance(body, bytes) or body == "{}"  # noqa: P103
            else {"json": body}
        )

        if schema_version_header:
            headers = defaultdict(dict, kwargs.get("headers", {}))
            headers.update({"Accept": schema_version_header})
            kwargs["headers"] = headers

        return self.post(
            path=RSACorePaths.POST_DATA.format(record_id=record_id),
            **body_kwarg,
            **kwargs,
        ).json()

    def get_measurements(
        self,
        record_id: str,
        dataset_id: str,
        schema_version_header: Optional[dict] = ACCEPT_HEADERS.format(version=SCHEMA_VERSION),
        columns_filter: Optional[str] = None,
        rows_filter: Optional[str] = None,
        columns_aggregation: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> Union[bytes, dict]:
        """
        :param record_id: created record id
        :param dataset_id: created dataset id
        :param schema_version_header: version of the dataset schema
        :param columns_filter: SampleDepth, Porosity, Lithology
        :param rows_filter: ex SampleDepth,lt,3900
                            lt - less than
                            lte - less than or equal to
                            gt - greater than

                            {"lt": "<", "gt": ">", "lte": "<=", "gte": ">=", "eq": "=", "neq": "!="}
        :param columns_aggregation: ex SampleDepth,avg. Possible values: [avg, count, max, min, sum]
        :param version:
        :param kwargs:
        :return: rca data
        """
        params_dict = {
            "columns_filter": columns_filter,
            "rows_filter": rows_filter,
            "columns_aggregation": columns_aggregation,
            "version": version,
        }

        if schema_version_header:
            headers = defaultdict(dict, kwargs.get("headers", {}))
            headers.update({"Accept": schema_version_header})
            kwargs["headers"] = headers

        response = self.get(
            path=RSACorePaths.GET_DATA.format(
                record_id=record_id,
                dataset_id=dataset_id,
            ),
            params=params_dict,
            **kwargs,
        )

        if response.headers["Content-Type"] == "application/x-parquet":
            return response.content
        elif response.headers["Content-Type"] == "application/json":
            return response.json()
        raise RuntimeError("Unknown content-type")

    def get_file(self, record_id: str, **kwargs) -> Response:
        """Get the file associated with a record.

        :param record_id: The ID of the record to retrieve the file for.
        :param kwargs: Additional keyword arguments.
        :return: The response object containing the file download.
        """
        return self.get(path=RSACorePaths.GET_FILE_DOWNLOAD.format(record_id=record_id), **kwargs)
