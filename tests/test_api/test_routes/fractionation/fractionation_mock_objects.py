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


TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:fractionation-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/fractionationdata/partition:work-product-component--SamplesAnalysis:fractionation_test/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v1/fractionationdata/partition:work-product-component--SamplesAnalysis:fractionation_test/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
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
    "columns_aggregation": "FractionationSum.Value,sum",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "SamplesAnalysisID,FractionationSum,AsphaltenePctOfExtract",
    "rows_filter": "SamplesAnalysisID,eq,opendes:work-product-component--SamplesAnalysis:FractionationDevTest:",
}

with open(f"{dir_path}/fractionation_orient_split.json") as fp:
    TEST_DATA = json.load(fp)

TEST_AGGREGATED_DATA = {
    "columns": [
        "FractionationSum",
    ],
    "index": [
        "sum",
    ],
    "data": [
        [
            0.169,
        ],
    ],
}

TEST_FILTERED_DATA = {
    "columns": [
        "SamplesAnalysisID",
        "FractionationSum",
        "AsphaltenePctOfExtract",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:FractionationDevTest:",
            {
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g:",
                "Value": 0.169,
            },
            {
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%25:",
                "Value": 0.756,
            },
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        "WrongField",  # Wrong field
        "data",
        # "SamplesAnalysisID",  # Missing mandatory field
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:1:",
            "opendes:master-data--:1:",  # Incorrect master-data value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting Permeability in index row 0
EXPECTED_ERROR_REASON = "Data error: 35 columns passed, passed data had 34 columns"


TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "SampleID,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "SampleID,wrong_operator,test_id"},
    {"rows_filter": "SamplesAnalysisID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "SamplesAnalysisID,wrong_operator"},
]
