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

from dataclasses import dataclass
from typing import Any, NamedTuple, Optional, Set

from loguru import logger
from pydantic.main import BaseModel


class Aggregation(NamedTuple):
    COMPARISON = {"lt": "<", "gt": ">", "lte": "<=", "gte": ">=", "eq": "=", "neq": "!="}
    OPERATORS = {"avg", "count", "max", "min", "sum"}
    N_ELEMENTS = 2


class Predicate(NamedTuple):
    OPERATORS = {"lt": "<", "gt": ">", "lte": "<=", "gte": ">=", "eq": "=", "neq": "!="}
    N_ELEMENTS = 3


class Projection(NamedTuple):
    STAR = "*"


class Separator(NamedTuple):
    DOT = "."
    COMMA = ","


@dataclass
class SQLFilterValidator:
    """Validation of query paramenters.

    :raises RuntimeError: If any validation error occurs
    :raises NotImplementedError: For not implemented features
    """
    model: BaseModel
    raw_columns_filter: Optional[str] = None
    raw_rows_filter: Optional[str] = None
    raw_columns_aggregation: Optional[str] = None

    @property
    def all_valid_columns(self) -> Set[str]:
        return set(self.model.__fields__.keys())

    @property
    def valid_columns_filter(self) -> str:
        columns_filter = Projection.STAR
        if self.raw_columns_filter:
            columns_filter = self._validate_columns_filter()
        return columns_filter

    @property
    def valid_rows_filter(self) -> str:
        rows_filter = None
        if self.raw_rows_filter:
            rows_filter = self._validate_rows_filter()
        return rows_filter

    @property
    def valid_columns_aggregation(self) -> str:
        columns_aggregation = None
        if self.raw_columns_aggregation:
            columns_aggregation = self._validate_columns_aggregation()
        return columns_aggregation

    def _validate_column_value(self, column: str, comp_value: Any) -> Any:
        logger.debug(f"TODO validate column: {column}")
        #  TODO swith to jsonschema validation since pydantic does not allow a clean per field validation
        return comp_value

    def _validate_aggregation_operator(self, operator: str) -> str:
        if operator not in Aggregation.OPERATORS:
            raise RuntimeError(f"Invalid aggregation operator not in: {Aggregation.OPERATORS}")
        return operator

    def _validate_comparison_operator(self, operator: str) -> str:
        operator = Predicate.OPERATORS.get(operator)
        if not operator:
            possible_operators = Predicate.OPERATORS.keys()
            raise RuntimeError(f"Invalid comparison operator not in: {possible_operators}")
        return operator

    def _validate_rows_filter(self) -> str:
        rows_filter_list = self.raw_rows_filter.split(Separator.COMMA)
        if len(rows_filter_list) != Predicate.N_ELEMENTS:
            raise RuntimeError("Bad rows_filter expression. Correct form 'ColumnName,operator,value'")
        if rows_filter_list[0].split(Separator.DOT)[0] not in self.all_valid_columns:
            raise RuntimeError(f"For filter select one of {self.all_valid_columns}")

        valid_column = self._handle_dotted_column(rows_filter_list[0])
        valid_operator = self._validate_comparison_operator(rows_filter_list[1])
        valid_value = self._handle_str_value(self._validate_column_value(valid_column, rows_filter_list[2]))
        return f"{valid_column} {valid_operator} {valid_value}"

    def _validate_columns_aggregation(self) -> str:
        columns_aggregation_list = self.raw_columns_aggregation.split(Separator.COMMA)
        if len(columns_aggregation_list) != Aggregation.N_ELEMENTS:
            raise RuntimeError("Bad aggregation expression. Correct form 'ColumnName,operator'")
        if columns_aggregation_list[0] not in self.all_valid_columns:
            raise RuntimeError(f"For aggregation select one of {self.all_valid_columns}")

        valid_column = self._handle_dotted_column(columns_aggregation_list[0])
        valid_operator = self._validate_aggregation_operator(columns_aggregation_list[1])
        return f"{valid_operator}({valid_column})"

    def _validate_columns_filter(self) -> str:
        raw_columns_filter_set = set(self.raw_columns_filter.split(Separator.COMMA))
        valid_columns = self.all_valid_columns.intersection(raw_columns_filter_set)
        columns_filter = Separator.COMMA.join(map(self._handle_dotted_column, valid_columns))
        invalid_columns = raw_columns_filter_set.difference(valid_columns)
        if invalid_columns:
            raise RuntimeError(f"Invalid columns: {invalid_columns}. Select one of {self.all_valid_columns}")
        return columns_filter

    def _handle_dotted_column(self, column: str) -> str:
        if Separator.DOT in column:
            #  TODO to be completed with above jsonschema validation
            logger.info(f"DOT in column: {column}")
        return column

    def _handle_str_value(self, comp_value: Any) -> str:
        logger.debug(type(comp_value))
        new_value = comp_value
        if isinstance(comp_value, str):
            new_value = f"'{comp_value}'"
        return new_value
