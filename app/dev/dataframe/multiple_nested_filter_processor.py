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

import pandas as pd

from app.dataframe.filter_processor import FilterProcessor
from app.dev.dataframe.multiple_nested_parquet_filter import (
    apply_filters_from_bytes,
    apply_filters_from_df,
)
from app.dev.resources.multiple_nested_filters import (
    DFMultipleNestedFilterValidator,
)


class DFMultipleNestedFilterProcessor(FilterProcessor):

    def __init__(
        self,
        df_filter: DFMultipleNestedFilterValidator,
    ):
        if not isinstance(df_filter, DFMultipleNestedFilterValidator):
            raise ValueError("Must be 'DFMultipleNestedFilterValidator' type")
        self._df_filter = df_filter

    @property
    def df_filter(self) -> DFMultipleNestedFilterValidator:
        return self._df_filter

    def apply_filters_from_bytes(self, parquet_bytes: bytes) -> pd.DataFrame:
        return apply_filters_from_bytes(parquet_bytes, self._df_filter)

    def apply_filters_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return apply_filters_from_df(df, self._df_filter)

    def get_filters_without_aggregation(self) -> "DFMultipleNestedFilterProcessor":
        df_filter_wo_agg = DFMultipleNestedFilterValidator(
            schema=self._df_filter.schema,
            raw_rows_filter=self._df_filter.raw_rows_filter,
            raw_columns_filter=self._df_filter.raw_columns_filter,
            raw_rows_multiple_filter=self._df_filter.raw_rows_multiple_filter,
        )
        return DFMultipleNestedFilterProcessor(df_filter_wo_agg)
