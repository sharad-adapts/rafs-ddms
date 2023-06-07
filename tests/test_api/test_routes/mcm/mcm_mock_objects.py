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
import os

from app.api.routes.mcm.api import BULK_DATASET_PREFIX, RECORD_TYPE
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
)

dir_path = os.path.dirname(os.path.abspath(__file__))
ddms_dataset_prefix = BULK_DATASET_PREFIX.replace("-", "")

TEST_DATASET_RECORD_ID = f"opendes:dataset--File.Generic:{BULK_DATASET_PREFIX}-123:test-version"
TEST_DDMS_URN = f"urn://rafs-v1/{ddms_dataset_prefix}data/partition:work-product-component--{RECORD_TYPE}:mcm_test/{TEST_DATASET_RECORD_ID}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "TestNumber,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "MultipleContactMiscibilityTestID,TestNumber,TestTemperature",
    "rows_filter": "MultipleContactMiscibilityTestID,eq,opendes:work-product-component--MultipleContactMiscibilityTest:mcm_test:",
}

TEST_DATA = {
    "columns": [
        "MultipleContactMiscibilityTestID",
        "FluidSampleID",
        "TestNumber",
        "TestTemperature",
        "TypeOfInjectedGas",
        "TypeOfMultiContactTest",
        "MolePctOfInjectedGas",
        "GasSolventCompositionReference",
        "MixRatio",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--MultipleContactMiscibilityTest:mcm_test:",
            "opendes:master-data--FluidSample:dd76cf6c-226f-5636-ad1b-1ca0f8249cc8:",
            "MCMT_222",
            {
                "Value": 243,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
            },
            "Regular",
            "Miscibility Test",
            {
                "Value": 22,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%mole:",
            },
            "CO2",
            235,
        ],
    ],
}

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
        "MultipleContactMiscibilityTestID",
        "TestNumber",
        "TestTemperature",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--MultipleContactMiscibilityTest:mcm_test:",
            "MCMT_222",
            {
                "Value": 243,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
            },
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        "WrongField",  # Wrong field
        "data",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--MultipleContactMiscibilityTest:1:",
            "opendes:master-data--:1:",  # Incorrect master-data value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting MixRatio
EXPECTED_ERROR_REASON = "Data error: 9 columns passed, passed data had 8 columns"


TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "TestNumber,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "TestNumber,wrong_operator,test_id"},
    {"rows_filter": "MultipleContactMiscibilityTestID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "MultipleContactMiscibilityTestID,wrong_operator"},
]
