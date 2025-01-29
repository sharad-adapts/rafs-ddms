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
from typing import List, Optional

import pandas as pd
import pyarrow as pa
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from loguru import logger
from pyarrow import parquet as pq

from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.dataframe.filter_processor import FilterProcessor
from app.dataframe.parquet_loader import DFPayload
from app.exceptions.exceptions import NotFoundException
from app.providers.dependencies.blob_storage import BlobMetadata, IBlobStorage
from app.resources.mime_types import SupportedMimeTypes


class BlobParquetLoader:

    @cache(expire=CACHE_DEFAULT_TTL, coder=PickleCoder)
    async def read_parquet_files(
        self,
        blob_ids: List[str],
        blob_storage_service: IBlobStorage,
        df_filter_processor: Optional[FilterProcessor] = None,
    ) -> List[DFPayload]:
        """Use blob storage service to read multiple parquet files.

        :param blobs_ids: the list of blobs ids
        :type blob_ids: List[str]
        :param df_filter: df_filter, defaults to None
        :type df_filter: Optional[DataFrameFilterValidator], optional
        :return: tuples of blob_id, pd.DataFrame, error message
        :rtype: List[DFPayload]
        """
        tasks = [
            self._read_parquet(
                blob_id=blob_id,
                blob_storage_service=blob_storage_service,
                df_filter_processor=df_filter_processor,
            )
            for blob_id in blob_ids
        ]
        return await asyncio.gather(*tasks)

    async def _read_parquet(  # noqa: WPS234
        self,
        blob_id: str,
        blob_storage_service: IBlobStorage,
        df_filter_processor: Optional[FilterProcessor] = None,
    ) -> DFPayload:
        """Read parquet file from blob metadata and apply df_filter."""
        analysis_family, analysis_type, version, uuid = blob_id.split("/")
        blob_metadata = BlobMetadata(
            analysis_family=analysis_family,
            analysis_type=analysis_type,
            version=version,
            uuid=uuid,
            content_type=SupportedMimeTypes.PARQUET,
        )
        try:
            blob = await blob_storage_service.get_blob(blob_metadata=blob_metadata)
            if df_filter_processor:
                df_filter_processor = df_filter_processor.get_filters_without_aggregation()
                df = df_filter_processor.apply_filters_from_bytes(blob.blob_data)
            else:
                df = pq.read_table(pa.BufferReader(blob.blob_data)).to_pandas()
            error_msg = None
        except NotFoundException as u_exc:
            object_name = blob_metadata.object_name
            error_msg = f"Unable to fetch: {object_name}. Not found, status code: {u_exc.status_code}"  # noqa: WPS237
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

        return DFPayload(blob_metadata.object_name, df, error_msg)
