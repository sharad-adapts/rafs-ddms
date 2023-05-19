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

from typing import Optional, Union

from requests import Response

from client.api_client import APIClient
from tests.test_api.api_version import API_VERSION


class RSACorePaths(object):
    COMMON_PART = f"/api/rafs-ddms/{API_VERSION}"
    POST_RSA = f"{COMMON_PART}/rocksampleanalyses"
    GET_RSA = f"{COMMON_PART}/rocksampleanalyses/{{record_id}}"
    POST_RCA = f"{COMMON_PART}/rocksampleanalyses/{{rsa_record_id}}/rca/data"
    GET_RCA = f"{COMMON_PART}/rocksampleanalyses/{{rsa_record_id}}/rca/data/{{rca_dataset_id}}"
    GET_VERSIONS = f"{COMMON_PART}/rocksampleanalyses/{{record_id}}/versions"
    GET_VERSION = f"{COMMON_PART}/rocksampleanalyses/{{record_id}}/versions/{{version}}"
    DELETE_RSA = f"{COMMON_PART}/rocksampleanalyses/{{record_id}}"
    GET_FILE_DOWNLOAD = f"{COMMON_PART}/rocksampleanalyses/{{record_id}}/rca/source"


class RSACore(APIClient):
    """API RSA methods."""

    def post_rsa_data(self, body: list, **kwargs) -> dict:
        """
        :param body: rsa data
        :return: created rsa
        """
        return self.post(path=RSACorePaths.POST_RSA, json=body, **kwargs).json()

    def get_rsa_data(
        self, record_id: str, version: Optional[str] = None, **kwargs,
    ) -> dict:
        """
        :param record_id: rsa record id
        :param version: rsa version
        :return: rsa data
        """
        params_dict = {"version": version}
        return self.get(
            path=RSACorePaths.GET_RSA.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def post_rca_data(self, rsa_record_id: str, body: dict, **kwargs) -> dict:
        """
        :param rsa_record_id: rsa_record_id from post_rsa
        :param body: rca data
        :return: created rca data
        """
        body_kwarg = (
            {"data": body}
            if isinstance(body, bytes) or body == "{}"  # noqa: P103
            else {"json": body}
        )
        return self.post(
            path=RSACorePaths.POST_RCA.format(rsa_record_id=rsa_record_id),
            **body_kwarg,
            **kwargs,
        ).json()

    def get_rca_data(
        self,
        rsa_record_id: str,
        rca_dataset_id: str,
        columns_filter: Optional[str] = None,
        rows_filter: Optional[str] = None,
        columns_aggregation: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs,
    ) -> Union[bytes, dict]:
        """
        :param rsa_record_id: created record id
        :param rca_dataset_id: created dataset id
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
        response = self.get(
            path=RSACorePaths.GET_RCA.format(
                rsa_record_id=rsa_record_id,
                rca_dataset_id=rca_dataset_id,
            ),
            params=params_dict,
            **kwargs,
        )

        if response.headers["Content-Type"] == "application/x-parquet":
            return response.content
        elif response.headers["Content-Type"] == "application/json":
            return response.json()
        raise RuntimeError("Unknown content-type")

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        return self.get(
            path=RSACorePaths.GET_VERSIONS.format(record_id=record_id),
            **kwargs,
        ).json()

    def get_version_of_the_record(self, record_id: str, version: int, **kwargs) -> dict:
        return self.get(
            path=RSACorePaths.GET_VERSION.format(record_id=record_id, version=version),
            **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        self.delete(path=RSACorePaths.DELETE_RSA.format(record_id=record_id), **kwargs)

    def get_rca_file(self, record_id: str, **kwargs) -> Response:
        return self.get(path=RSACorePaths.GET_FILE_DOWNLOAD.format(record_id=record_id), **kwargs)
