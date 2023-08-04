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

from typing import List, Optional

from app.core.settings.app import AppSettings
from app.models.schemas.user import User
from app.services.base import ISearchService
from app.services.osdu_clients.search_client import SearchServiceApiClient


class SearchService(ISearchService):

    def __init__(
        self,
        data_partition_id: str,
        settings: AppSettings,
        user: User,
        extra_headers: dict,
    ) -> None:
        self.search_client = SearchServiceApiClient(
            settings.service_host_search,
            data_partition_id=data_partition_id,
            bearer_token=user.access_token,
            extra_headers=extra_headers,
        )

    async def find_records(
        self,
        kind: Optional[str] = "*:*:*:*",
        query: Optional[str] = "*",
        limit: Optional[int] = None,
        **kwargs,
    ) -> List[dict]:
        """Find records.

        :param kind: kinf of record, defaults to "*:*:*:*"
        :type kind: str, optional
        :param query: query, defaults to "*"
        :type query: str, optional
        :param limit: limit, defaults to None
        :type limit: int, optional
        :return: records
        :rtype: List[dict]
        """
        return await self.search_client.query({
            **{
                "kind": kind,
                "query": query,
                "limit": limit,
            }, **kwargs,
        })
