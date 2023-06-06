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

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:compositionalanalysis-123:1234"
TEST_DDMS_URN = f"urn://rafs-v1/compositionalanalysisdata/partition:work-product-component--CompositionalAnalysisTest:compositionalanalysis_test/{TEST_DATASET_RECORD_ID}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "CompositionalAnalysisTestID,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "CompositionalAnalysisTestID",
    "rows_filter": "CompositionalAnalysisTestID,eq,opendes:work-product-component--CompositionalAnalysisTest:1:",
}

TEST_DATA = {
    "columns": [
        "CompositionalAnalysisTestID",
        "TestNumber",
        "FluidSampleID",
        "CompositionalAnalysis",
        "CalculatedProperties",
        "GasCompositionalCalculations",
        "OilCompositionalCalculations",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--CompositionalAnalysisTest:1:",
            "1",
            "opendes:master-data--FluidSample:1:",
            {
                "СomponentFormula": "C1",
                "ComponentName": "Methane",
                "FlashedLiquidRelativeMolarWeight": {
                    "Value": 16.04,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure: %[molar]",
                },
                "FlashedLiquidRelativeMass": {
                    "Value": 16.04,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure: %[mass]",
                },
                "FlashedGasRelativeMolarWeight": {
                    "Value": 16.04,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure: %[molar]",
                },
                "OverallFluidRelativeMolarWeight": {
                    "Value": 16.04,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure: %[molar]",
                },
                "OverallFluidRelativeMass": {
                    "Value": 16.04,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure: %[mass]",
                },
            },
            {
                "AvgFlashedFluidMoleWeight": {
                    "Value": 25.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                },
                "AvgFlashedGasMoleWeight": {
                    "Value": 35.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mass]",
                },
                "AvgFlashedOverallFluidMoleWeight": {
                    "Value": 38.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mass]",
                },
                "FlashedLiquidDensity": {
                    "Value": 15.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "FlashedGasDensity": {
                    "Value": 25.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "OverallFluidDensity": {
                    "Value": 50.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "FlashedLiquidRealRelativeDensity": {
                    "Value": 0.08,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "FlashedGasRealRelativeDensity": {
                    "Value": 0.25,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "OverallFluidRealRelativeDensity": {
                    "Value": 0.63,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3",
                },
                "FlashedLiquidGasOilRatio": {
                    "Value": 50.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:scf/bbl",
                },
                "FlashedGasOilRatio": {
                    "Value": 50.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:scf/bbl",
                },
                "OverallLiquidGasOilRatio": {
                    "Value": 50.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:scf/bbl",
                },
                "FlashedLiquidMoleFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "FlashedGasMoleFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "OverallLiquidMoleFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "FlashedLiquidMassFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "FlashedGasMassFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "OverallLiquidMassFraction": {
                    "Value": 33.0,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%",
                },
                "SampleCalculatedProperties": [{
                    "ComponentFormula": "C10H22",
                    "ComponentName": "Decane",
                    "FlashedLiquidRelativeMolarWeight": {
                        "Value": 142.48,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "FlashedLiquidMolecularWeight": {
                        "Value": 64.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "FlashedLiquidDensity": {
                        "Value": 142.48,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[density]",
                    },
                    "FlashedGasMolecularWeight": {
                        "Value": 142.48,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "FlashedGasRelativeMolarWeight": {
                        "Value": 55.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "FlashedGasDensity": {
                        "Value": 0.085,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[density]",
                    },
                    "OverallFluidMolecularWeight": {
                        "Value": 75.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "OverallFluidRelativeWeight": {
                        "Value": 71.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                    "OverallFluidDensity": {
                        "Value": 0.0854,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:%[mole]",
                    },
                }],
            },
            [{
                "ComponentName": "Hydrogen",
                "MoleWeight": {
                    "Value": 2.016,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/mol:",
                },
                "Density": {
                    "Value": 0.8006,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3:",
                },
            }],
            [{
                "ComponentName": "Hydrogen",
                "MoleWeight": {
                    "Value": 2.016,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/mol:",
                },
                "Density": {
                    "Value": 0.8006,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:g/cm3:",
                },
            }],
        ],
    ],
}

TEST_AGGREGATED_DATA = {
    "columns": [
        "count(\"CompositionalAnalysisTestID\")",
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
        "CompositionalAnalysisTestID",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--CompositionalAnalysisTest:1:",
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        # "CompositionalAnalysisTestID",  # Missing mandatory field
        "WrongField",  # Wrong field
        "TestNumber",
        "FluidSampleID",
        "CompositionalAnalysis",
        "CalculatedProperties",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--CCEMeasurements:1:",
            "1",
            "opendes:master-data--:1:",  # Incorrect Value
            [],
            [],
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
