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

from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
)

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:capillary-pressure-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/capillarypressuredata/partition:work-product-component--SamplesAnalysis:cappressure_test/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v1/capillarypressuredata/partition:work-product-component--SamplesAnalysis:cappressure_test/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
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
    "columns_aggregation": "SamplesAnalysisID,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "SamplesAnalysisID",
    "rows_filter": "SamplesAnalysisID,eq,opendes:work-product-component--SamplesAnalysis:1:",
}

TEST_DATA = {
    "columns": [
        "SamplesAnalysisID",
        "TestData",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:1:",
            [
                {
                    "SampleID": "opendes:master-data--Sample:1:",
                    "Depth": {
                        "Value": 5293.22,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:m:",
                    },
                    "Permeability": {
                        "Value": 52.2,
                        "Type": "opendes:reference-data--PermeabilityMeasurementType:Kair:",
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:md:",
                    },
                    "Porosity": {
                        "Value": 0.266,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "InitialSaturation": {
                        "Value": 1,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "Remark": "Test was successfully executed",
                    "CapPressureSteps": [
                        {
                            "StepNumber": "1",
                            "CapPressure": {
                                "Value": 2,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "WaterSaturation": {
                                "Value": 0.978,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                            },
                        },
                        {
                            "StepNumber": "2",
                            "CapPressure": {
                                "Value": 1440,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "WaterSaturation": {
                                "Value": 0.937,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                            },
                        },
                    ],
                },
                {
                    "SampleID": "opendes:master-data--Sample:2:",
                    "Depth": {
                        "Value": 5293.53,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:m:",
                    },
                    "Permeability": {
                        "Value": 88.4,
                        "Type": "opendes:reference-data--PermeabilityMeasurementType:Kair:",
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:md:",
                    },
                    "Porosity": {
                        "Value": 0.279,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "InitialSaturation": {
                        "Value": 1,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "Remark": "Test was successfully executed",
                    "CapPressureSteps": [
                        {
                            "StepNumber": "1",
                            "CapPressure": {
                                "Value": 2,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "WaterSaturation": {
                                "Value": 0.978,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                            },
                        },
                        {
                            "StepNumber": "2",
                            "CapPressure": {
                                "Value": 1450,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "WaterSaturation": {
                                "Value": 0.968,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                            },
                        },
                    ],
                },
            ],
        ],
    ],
}

TEST_AGGREGATED_DATA = {
    "columns": [
        "count(\"SamplesAnalysisID\")",
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
        "SamplesAnalysisID",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:1:",
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        # "SamplesAnalysisID",  # Missing mandatory field
        "TestData",
        "WrongField",  # Wrong field
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysisID:1:",
            {},  # Incorrect value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting DifferentialLiberationTestSteps
EXPECTED_ERROR_REASON = f"Data error: {len(INCORRECT_DATAFRAME_TEST_DATA['columns'])} columns passed, " \
                        f"passed data had {len(INCORRECT_DATAFRAME_TEST_DATA['data'][0])} columns"


TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "SamplesAnalysisID,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "SamplesAnalysisID,wrong_operator,test_id"},
    {"rows_filter": "SamplesAnalysisID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "SamplesAnalysisID,wrong_operator"},
]
