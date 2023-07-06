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

import copy
import json
import os

from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
)

dir_path = os.path.dirname(os.path.abspath(__file__))

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:multi-stage-separator-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/multistageseparatordata/partition:work-product-component--MultiStageSeparatorTest:multistageseparator_test/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v1/multistageseparatordata/partition:work-product-component--MultiStageSeparatorTest:multistageseparator_test/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
RECORD_DATA_WITH_SCHEMA_VERSION = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN_WITH_VERSION],
        },
    },
}
RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [f"{TEST_DDMS_URN}/2.0.0"],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "TestNumber,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "MultiStageSeparatorTestID,TestNumber,ReservoirTemperature",
    "rows_filter": "MultiStageSeparatorTestID,eq,opendes:work-product-component--MultiStageSeparatorTest:mss_test:",
}

with open(f"{dir_path}/mss_data_orient_split.json") as fp:
    TEST_DATA = json.load(fp)

TEST_AGGREGATED_DATA = {
    "columns": [
        "count(\"TestNumber\")",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            1,
        ],
    ],
}

TEST_FILTERED_DATA = {
    "columns": [
        "MultiStageSeparatorTestID",
        "TestNumber",
        "ReservoirTemperature",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--MultiStageSeparatorTest:mss_test:",
            "752156",
            {
                "Value": 75,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
            },
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        "WrongField",  # Wrong field
        "data",
        # "MultiStageSeparatorTestSteps",  # Missing mandatory field
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--MultiStageSeparatorTest:1:",
            "opendes:master-data--:1:",  # Incorrect Coring value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting MultiStageSeparatorTestSteps
EXPECTED_ERROR_REASON = "Data error: 15 columns passed, passed data had 14 columns"


TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "TestNumber,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "TestNumber,wrong_operator,test_id"},
    {"rows_filter": "MultiStageSeparatorTestID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "MultiStageSeparatorTestID,wrong_operator"},
]
