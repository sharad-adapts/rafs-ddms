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

from abc import ABC, abstractmethod

import pandas as pd

from app.dataframe.parquet_filter import (
    apply_filters_from_bytes,
    apply_filters_from_df,
)
from app.resources.filters import DataFrameFilterValidator


class FilterProcessor(ABC):

    @abstractmethod
    def apply_filters_from_bytes(self, parquet_bytes: bytes) -> pd.DataFrame:
        """_summary_

        :param parquet_bytes: _description_
        :type parquet_bytes: _type_
        :return: _description_
        :rtype: pd.DataFrame
        """

    @abstractmethod
    def apply_filters_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """_summary_

        :param df: _description_
        :type df: pd.DataFrame
        :return: _description_
        :rtype: pd.DataFrame
        """

    @abstractmethod
    def get_filters_without_aggregation(self) -> "FilterProcessor":
        """_summary_

        :raises ValueError: _description_
        :return: _description_
        :rtype: DataFrameFilterApplier
        """


class DFFilterProcessor(FilterProcessor):

    def __init__(
        self,
        df_filter: DataFrameFilterValidator,
    ):
        if not isinstance(df_filter, DataFrameFilterValidator):
            raise ValueError("Must be 'DataFrameFilterValidator' type")
        self._df_filter = df_filter

    @property
    def df_filter(self) -> DataFrameFilterValidator:
        return self._df_filter

    def apply_filters_from_bytes(self, parquet_bytes: bytes) -> pd.DataFrame:
        return apply_filters_from_bytes(parquet_bytes, self._df_filter)

    def apply_filters_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return apply_filters_from_df(df, self._df_filter)

    def get_filters_without_aggregation(self) -> "DFFilterProcessor":
        df_filter_wo_agg = DataFrameFilterValidator(
            model=self._df_filter.model,
            raw_rows_filter=self._df_filter.raw_rows_filter,
            raw_columns_filter=self._df_filter.raw_columns_filter,
        )
        return DFFilterProcessor(df_filter_wo_agg)
