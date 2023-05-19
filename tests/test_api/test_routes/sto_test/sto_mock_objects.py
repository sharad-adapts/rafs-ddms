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

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:stoanalysis-123:test-version"
TEST_DDMS_URN = f"urn://rafs-v1/stoanalysisdata/partition:work-product-component--StockTankOilAnalysisTest:sto_test/{TEST_DATASET_RECORD_ID}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "StockTankOilAnalysisTestID,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "StockTankOilAnalysisTestID",
    "rows_filter": "StockTankOilAnalysisTestID,eq,opendes:work-product-component--StockTankOilAnalysisTest:1:",
}

TEST_DATA = {
    "index": [0],
    "columns": [
        "StockTankOilAnalysisTestID",
        "FluidConditions",
        "PhasesPresent",
        "STOFLashedLiquidProperties",
        "SARA",
        "HTGCAnalysis",
    ],
    "data": [
        [
            "opendes:work-product-component--StockTankOilAnalysisTest:1:",
            "stock tank conditions",
            "oil",
            [{
                "SampleDepth": {
                    "Value": 5210.2,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:mMD:",
                },
                "OilAPIGravity": {
                    "Value": 30,

                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:dAPI:",
                },
                "WaterContent": {
                    "Value": 0.5,

                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "WatsonKFactor": 117,
                "AsphaltaneContent": {
                    "Value": 3.22,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "ParrafinContent": {
                    "Value": 0.07,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "CloudPoint": {
                    "Value": 35,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
                "WaxContent": {
                    "Value": 0.76,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "WaxAppearanceTemperature": {
                    "Value": 101.5,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
                "Saturates": {
                    "Value": 51.1,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "PourPoint": {
                    "Value": 14,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
                "ASTMFlashPoint": {
                    "Value": 80,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
                "TotalAcidNumber": {
                    "Value": 0.1,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:KOH/g:",
                },
                "TotalSulfurContent": {
                    "Value": 0.546,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "NBase": {
                    "Value": 553,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ppm:",
                },
                "NitrogenContent": {
                    "Value": 0.1,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "ElementalSulfurContent": {
                    "Value": 0.05,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "LeadContent": {
                    "Value": 0.001,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "NickelContent": {
                    "Value": 0.009,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "VanadiumContent": {
                    "Value": 0.0001,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "IronContent": {
                    "Value": 0.0001,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "ViscosityAtTemperature": {
                    "Value": 10,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
                "ReidVaporPressure": {
                    "Value": 1.26,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psi:",
                },
            }],
            [{
                "AromaticsWeightFraction": {
                    "Value": 15,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "AsphaltenesWeightFraction": {
                    "Value": 15,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "NapthenesWeightFraction": {
                    "Value": 12,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "ParaffinsWeightFraction": {
                    "Value": 19,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                },
                "SaturationPressure": {
                    "Value": 8000,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                },
                "SaturationTemperature": {
                    "Value": 220,
                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:degF:",
                },
            }],
            [
                {
                    "CarbonNumber": "C20",
                    "ParaffinContent": {
                        "Value": 2786.3,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ppm:",
                    },
                    "ParaffinWeightFraction": {
                        "Value": 0.2786,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                    },
                    "CumulativeParaffinFraction": {
                        "Value": 0.2786,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                    },
                },
                {
                    "CarbonNumber": "C21",
                    "ParaffinContent": {
                        "Value": 2431.3,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ppm:",
                    },
                    "ParaffinWeightFraction": {
                        "Value": 0.2431,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                    },
                    "CumulativeParaffinFraction": {
                        "Value": 0.5218,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:wtpct:",
                    },
                },
            ],
        ],
    ],
}

TEST_AGGREGATED_DATA = {
    "columns": [
        "count(\"StockTankOilAnalysisTestID\")",
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
        "StockTankOilAnalysisTestID",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--StockTankOilAnalysisTest:1:",
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        # "StockTankOilAnalysisTestID",  # Missing mandatory field
        "WrongField",  # Wrong field
        "FluidSampleID",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--CCEMeasurements:1:",
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
