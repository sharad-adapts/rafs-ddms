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

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:constantvolumedepletiontest-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/constantvolumedepletiontestdata/partition:work-product-component--ConstantVolumeDepletionTest:cvd_test/{TEST_DATASET_RECORD_ID}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "ConstantVolumeDepletionTestID,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "ConstantVolumeDepletionTestID",
    "rows_filter": "ConstantVolumeDepletionTestID,eq,opendes:work-product-component--ConstantVolumeDepletionTest:1:",
}

TEST_DATA = {
    "columns": [
        "ConstantVolumeDepletionTestID",
        "TestNumber",
        "FluidSampleID",
        "VaporProperties",
        "LiquidProperties",
        "FluidComposition",
        "CalculatedTotalProperties",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--ConstantVolumeDepletionTest:1:",
            "1",
            "opendes:master-data--FluidSample:1:",
            [
                {
                    "StepNumber": "1",
                    "StepPressure": {
                        "Value": 5000,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psi:",
                    },
                    "GasDensity": {
                        "Value": 0.504,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3:",
                    },
                    "GasPhaseZFactor": 1.692,
                    "TwoPhaseZFactor": 1.692,
                    "GasMoleWeight": {
                        "Value": 39.73,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:mole:",
                    },
                    "GasViscosity": {
                        "Value": 0.108,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:cP:",
                    },
                    "GasFVF": {
                        "Value": 605,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:Bg:",
                    },
                },
            ],
            [
                {
                    "StepNumber": "1",
                    "StepPressure": {
                        "Value": 5000,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psi:",
                    },
                    "MolesDisplaced": {
                        "Value": 0.0008,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
                    },
                    "ReservoirFluidDisplaced": {
                        "Value": 0.0008,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%:",
                    },
                    "ReservoirLiquidVolume": {
                        "Value": 0.0008,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%:",
                    },
                    "SaturationLiquidVolume": {
                        "Value": 0.0008,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
                    },
                    "AbsoluteLiquidVolume": {
                        "Value": 0.0008,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%:",
                    },
                },
            ],
            [
                {
                    "ComponentName": "C12+",
                    "StepPressure": {
                        "Value": 5000,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psi:",
                    },
                    "RelativeMoleWeight": {
                        "Value": 74.68,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
                    },
                    "LiquidFraction": {
                        "Value": 74.68,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
                    },
                },
            ],
            [
                {
                    "StepNumber": "1",
                    "StepPressure": {
                        "Value": 5000,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psi:",
                    },
                    "MoleWeight": {
                        "Value": 26.99,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
                    },
                    "GasGravity": 1.372,
                    "ZFactor": 1.413,
                    "ComponentMoleWeight": [
                        {
                            "ComponentName": "C10+",
                            "MoleWeight": {
                                "Value": 247.01,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]:",
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
        "count(\"ConstantVolumeDepletionTestID\")",
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
        "ConstantVolumeDepletionTestID",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--ConstantVolumeDepletionTest:1:",
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        # "ConstantVolumeDepletionTestID",  # Missing mandatory field
        "WrongField",  # Wrong field
        "TestNumber",
        "FluidSampleID",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--CCEMeasurements:1:",
            "1",
            "opendes:master-data--:1:",  # Incorrect Value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()
EXPECTED_ERROR_REASON = f"Data error: {len(INCORRECT_DATAFRAME_TEST_DATA['columns'])} columns passed, " \
                        f"passed data had {len(INCORRECT_DATAFRAME_TEST_DATA['data'][0])} columns"

TEST_WRONG_COLUMNS_FILTERS = [
    {"columns_filter": "unvalid_column_1,unvalid_column_2"},
    {"columns_filter": "FluidSampleID,"},
]
TEST_WRONG_ROWS_FILTERS = [
    {"rows_filter": "wrong_syntax"},
    {"rows_filter": "unvalid_column,gt,0"},
    {"rows_filter": "FluidSampleID,wrong_operator,test_id"},
    {"rows_filter": "FluidSampleID,eq,wrong_pattern"},
]
TEST_WRONG_AGGREGATION = [
    {"columns_aggregation": "wrong_syntax"},
    {"columns_aggregation": "unvalid_column,avg"},
    {"columns_aggregation": "FluidSampleID,wrong_operator"},
]
