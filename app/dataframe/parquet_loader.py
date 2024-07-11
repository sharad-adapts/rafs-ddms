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
from typing import List, NamedTuple, Optional, Tuple

import httpx
import pandas as pd
import pyarrow as pa
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from loguru import logger
from pyarrow import parquet as pq

from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.dataframe.filter_processor import FilterProcessor

RETRIES = 3


class DFPayload(NamedTuple):
    dataset_id: str
    df: pd.DataFrame
    error_msg: Optional[str]


class ParquetLoader:

    @cache(expire=CACHE_DEFAULT_TTL, coder=PickleCoder)
    async def read_parquet_files(
        self,
        signed_urls: List[Tuple[str, str]],
        df_filter_processor: Optional[FilterProcessor] = None,
    ) -> List[DFPayload]:
        """Use asynchronous HTTP requests to read multiple parquet files from
        signed urls.

        :param signed_urls: pairs of dataset, signed_url
        :type signed_urls: List[Tuple[str, str]]
        :param df_filter: df_filter, defaults to None
        :type df_filter: Optional[DataFrameFilterValidator], optional
        :return: pairs of dataset_id, pd.DataFrame
        :rtype: List[DFPayload]
        """
        transport = httpx.AsyncHTTPTransport(retries=RETRIES)
        async with httpx.AsyncClient(transport=transport) as client:
            tasks = [
                self._read_parquet_from_url(dataset_id, url, df_filter_processor, client)
                for (dataset_id, url) in signed_urls
            ]
            return await asyncio.gather(*tasks)

    async def _read_parquet_from_url(  # noqa: WPS234
        self,
        dataset_id: str,
        url: str,
        df_filter_processor: Optional[FilterProcessor] = None,
        client: httpx.AsyncClient = None,
    ) -> DFPayload:
        """Read parquet file from url and apply df_filter."""
        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                read_content = await response.aread()
                if df_filter_processor:
                    df_filter_processor = df_filter_processor.get_filters_without_aggregation()
                    df = df_filter_processor.apply_filters_from_bytes(read_content)
                else:
                    df = pq.read_table(pa.BufferReader(read_content)).to_pandas()
                error_msg = None
        except httpx.HTTPStatusError as http_exc:
            error_msg = f"HTTP status error {http_exc.response.status_code} for URL: {url}"  # noqa: WPS237
            logger.error(error_msg)
            df = pd.DataFrame()
        except httpx.RequestError as req_exc:
            error_msg = f"Request error for URL: {url} - {req_exc}"
            logger.error(error_msg)
            df = pd.DataFrame()
        except (
            pa.lib.ArrowCancelled,
            pa.lib.ArrowCapacityError,
            pa.lib.ArrowException,
            pa.lib.ArrowKeyError,
            pa.lib.ArrowIndexError,
            pa.lib.ArrowInvalid,
            pa.lib.ArrowIOError,
            pa.lib.ArrowMemoryError,
            pa.lib.ArrowNotImplementedError,
            pa.lib.ArrowTypeError,
            pa.lib.ArrowSerializationError,
        ) as exc:
            error_msg = f"PyArrowException: {exc}"
            logger.error(error_msg)
            df = pd.DataFrame()

        return DFPayload(dataset_id, df, error_msg)
