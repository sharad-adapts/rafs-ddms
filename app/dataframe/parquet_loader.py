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

import asyncio
from typing import List, Optional, Tuple

import httpx
import pandas as pd
import pyarrow as pa
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from loguru import logger
from pyarrow import parquet as pq

from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.dataframe.parquet_filter import (
    DataFrameFilterValidator,
    apply_filters_from_bytes,
)


class ParquetLoader:

    @cache(expire=CACHE_DEFAULT_TTL, coder=PickleCoder)
    async def read_parquet_files(
        self,
        signed_urls: List[Tuple[str, str]],
        df_filter: Optional[DataFrameFilterValidator] = None,
    ) -> List[Tuple[str, pd.DataFrame]]:
        """Use asynchronous HTTP requests to read multiple parquet files from
        signed urls.

        :param signed_urls: pairs of dataset, signed_url
        :type signed_urls: List[Tuple[str, str]]
        :param df_filter: df_filter, defaults to None
        :type df_filter: Optional[DataFrameFilterValidator], optional
        :return: pairs of dataset_id, pd.DataFrame
        :rtype: List[Tuple[str, pd.DataFrame]]
        """
        async with httpx.AsyncClient() as client:
            tasks = [
                self._read_parquet_from_url(dataset_id, url, df_filter, client)
                for (dataset_id, url) in signed_urls
            ]
            return await asyncio.gather(*tasks)

    async def _read_parquet_from_url(
        self,
        dataset_id: str,
        url: str,
        df_filter: Optional[DataFrameFilterValidator] = None,
        client: httpx.AsyncClient = None,
    ) -> Optional[Tuple[str, pd.DataFrame]]:
        """Read parquet file from url and apply df_filter."""
        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                read_content = await response.aread()
                df = apply_filters_from_bytes(read_content, df_filter) if df_filter else pq.read_table(
                    pa.BufferReader(read_content),
                ).to_pandas()
                return dataset_id, df
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP status error {exc.response.status_code} for URL: {url}")  # noqa: WPS237
        except httpx.RequestError as exc:
            logger.error(f"Request error for URL: {url} - {exc}")
