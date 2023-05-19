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

from contextlib import contextmanager

import duckdb
import pandas as pd
import pyarrow as pa
from fastapi import HTTPException
from pyarrow import parquet as pq

from app.resources.filters import SQLFilterValidator


@contextmanager
def duckdb_connection():
    conn = duckdb.connect()
    try:
        yield conn
    finally:
        conn.close()


def apply_filters(
    parquet_bytes: bytes,
    sql_filter: SQLFilterValidator,
) -> pd.DataFrame:
    """_summary_

    :param bytes parquet_bytes: parquet as read from blob storage
    :param SQLFilter filter: sql filter validator
    :return pd.DataFrame: the pd.DataFrame result from applying filters
    """
    with duckdb_connection() as conn:
        rel = conn.from_arrow(pq.read_table(pa.BufferReader(parquet_bytes)))

        try:
            if sql_filter.valid_columns_aggregation:
                aggregated_rel = rel.aggregate(sql_filter.valid_columns_aggregation)
                df = aggregated_rel.df()
            else:
                filtered_rel = rel.filter(sql_filter.valid_rows_filter) if sql_filter.valid_rows_filter else rel
                projected_rel = filtered_rel.project(sql_filter.valid_columns_filter)
                df = projected_rel.df()
        except duckdb.BinderException as err:
            raise HTTPException(status_code=422, detail=str(err))

        return df
