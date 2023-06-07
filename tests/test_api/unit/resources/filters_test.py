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

import re

import pytest
from pydantic.main import BaseModel

from app.models.domain.osdu.base import PATH_TO_DATA_MODEL
from app.resources.filters import SQLFilterValidator


class NestedModel(BaseModel):
    nested_field: str


class MockModel(BaseModel):
    field1: str
    field2: int
    field3: NestedModel


def test_valid_columns_filter():
    validator = SQLFilterValidator(MockModel, raw_columns_filter="field1,field2")
    assert validator.valid_columns_filter == "field1,field2"


@pytest.mark.parametrize("raw_columns_filter", ["field1,field4", "field2,"])
def test_valid_columns_filter_invalid_columns(raw_columns_filter):
    validator = SQLFilterValidator(MockModel, raw_columns_filter=raw_columns_filter)
    with pytest.raises(RuntimeError) as exc_info:
        validator.valid_columns_filter
    assert re.match(r"Invalid columns: {'.*'}. Select one of {.+}", str(exc_info.value))


def test_valid_rows_filter():
    validator = SQLFilterValidator(MockModel, raw_rows_filter="field1,eq,value1")
    assert validator.valid_rows_filter == "field1 = 'value1'"

    nested_validator = SQLFilterValidator(MockModel, raw_rows_filter="field3.nested_field,eq,value1")
    assert nested_validator.valid_rows_filter == "field3.nested_field = 'value1'"


def test_valid_rows_filter_invalid_format():
    validator = SQLFilterValidator(MockModel, raw_rows_filter="field1,eq")
    with pytest.raises(RuntimeError) as exc_info:
        validator.valid_rows_filter
    assert str(exc_info.value) == "Bad rows_filter expression. Correct form 'ColumnName[.FieldName],operator,value'"


def test_valid_columns_aggregation():
    validator = SQLFilterValidator(MockModel, raw_columns_aggregation="field1,avg")
    assert validator.valid_columns_aggregation == "avg(field1)"

    nested_validator = SQLFilterValidator(MockModel, raw_columns_aggregation="field3.nested_field,count")
    assert nested_validator.valid_columns_aggregation == "count(field3.nested_field)"


def test_valid_columns_aggregation_invalid_format():
    validator = SQLFilterValidator(MockModel, raw_columns_aggregation="field1")
    with pytest.raises(RuntimeError) as exc_info:
        validator.valid_columns_aggregation
    assert str(exc_info.value) == "Bad aggregation expression. Correct form 'ColumnName[.FieldName],operator'"


def test_valid_columns_aggregation_invalid_operator():
    validator = SQLFilterValidator(MockModel, raw_columns_aggregation="field1,average")
    with pytest.raises(RuntimeError) as exc_info:
        validator.valid_columns_aggregation
    assert re.match(r"Invalid aggregation operator not in: {.+}", str(exc_info.value))


def test_invalid_aggregatiom_dotted_colums():
    nested_aggregation_validator = SQLFilterValidator(
        MockModel, raw_columns_aggregation="field3.,avg", raw_rows_filter="field3.,eq,test",
    )

    with pytest.raises(RuntimeError) as exc_info:
        nested_aggregation_validator.valid_columns_aggregation
    assert str(exc_info.value) == "Wrong Column or Field name syntax: correct form: {ColumnName.FieldName}"

    with pytest.raises(RuntimeError) as exc_info:
        nested_aggregation_validator.valid_rows_filter
    assert str(exc_info.value) == "Wrong Column or Field name syntax: correct form: {ColumnName.FieldName}"
