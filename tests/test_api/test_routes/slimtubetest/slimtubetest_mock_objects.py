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

from app.api.routes.slimtubetest.api import BULK_DATASET_PREFIX
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
    TEST_SLIMTUBETEST_ID,
)

dir_path = os.path.dirname(os.path.abspath(__file__))

TEST_DATASET_RECORD_ID = f"opendes:dataset--File.Generic:{BULK_DATASET_PREFIX}-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/slimtubetestdata/{TEST_SLIMTUBETEST_ID}/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v1/slimtubetestdata/{TEST_SLIMTUBETEST_ID}/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
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
    "columns_filter": "SlimTubeTestID,FluidSampleID,TestNumber,MinimumMiscibilityPressure",
    "rows_filter": "SlimTubeTestID,eq,opendes:work-product-component--SlimTubeTest:slimtube_test:",
}

with open(f"{dir_path}/slimtube_data_orient_split.json") as fp:
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
        "SlimTubeTestID",
        "FluidSampleID",
        "TestNumber",
        "MinimumMiscibilityPressure",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SlimTubeTest:slimtube_test:",
            "opendes:master-data--FluidSample:fluid_sample_test:",
            "SlimTube_123",
            {
                "Value": 524.8,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:bar:",
            },
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        "WrongField",  # Wrong field
        "FluidSampleID",
        # "SlimTubeTestID",  # Missing mandatory field
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--SlimTubeTest:1:",
            "opendes:master-data--:1:",  # Incorrect fluid sample value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting SlimTubeTestID
EXPECTED_ERROR_REASON = "Data error: 15 columns passed, passed data had 14 columns"


TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "TestNumber,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "TestNumber,wrong_operator,test_id"},
    {"rows_filter": "SlimTubeTestID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "SlimTubeTestID,wrong_operator"},
]
