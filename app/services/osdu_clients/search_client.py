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

from typing import NamedTuple

import httpx

from app.resources.common_headers import (
    AUTHORIZATION,
    CONTENT_TYPE,
    DATA_PARTITION_ID,
)


class SearchServicePaths(NamedTuple):
    QUERY = "/query"
    CURSOR_QUERY = "/query_with_cursor"


class SearchServiceApiClient(object):
    def __init__(self, base_url: str, *, data_partition_id: str = None, bearer_token: str = None) -> None:
        self.base_url = base_url
        self.headers = {
            CONTENT_TYPE: "application/json",
            DATA_PARTITION_ID: data_partition_id,
            AUTHORIZATION: f"Bearer {bearer_token}",
        }

    def add_headers(self, headers: dict) -> None:
        """Add headers.

        :param headers: headers
        :type headers: dict
        """
        self.headers = {**self.headers, **headers}

    async def query(self, query: dict) -> dict:
        """Performa query to the osdu search service.

        :param query: query
        :type query: dict
        :return: query result
        :rtype: dict
        """
        async with httpx.AsyncClient(base_url=self.base_url, headers=self.headers) as client:
            response = await client.post(SearchServicePaths.QUERY, json=query, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def query_with_cursor(self, query: dict) -> dict:
        """Performa query to the osdu search service.

        :param query: query
        :type query: dict
        :return: query with cursor result
        :rtype: dict
        """
        async with httpx.AsyncClient(base_url=self.base_url, headers=self.headers) as client:
            response = await client.post(SearchServicePaths.CURSOR_QUERY, json=query, headers=self.headers)
            response.raise_for_status()
            return response.json()
