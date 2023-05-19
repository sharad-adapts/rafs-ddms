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

from app.models.data_schemas.cce_data_model import (
    FluidConditionType,
    PhasesPresentType,
)
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    OSDU_GENERIC_RECORD,
)

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:constant-composition-expansion-123:test-version"
TEST_DDMS_URN = f"urn://rafs-v1/constantcompositionexpansiondata/partition:work-product-component--ConstantCompositionExpansionTest:cce-test/{TEST_DATASET_RECORD_ID}"
RECORD_DATA = {
    **OSDU_GENERIC_RECORD.dict(exclude_none=True), **{
        "data": {
            "DDMSDatasets": [TEST_DDMS_URN],
        },
    },
}
TEST_PARAMS_AGGREGATION = {
    "columns_aggregation": "ConstantCompositionExpansionTestSteps,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "ConstantCompositionExpansionTestID",
    "rows_filter": "ConstantCompositionExpansionTestID,eq,opendes:work-product-component--ConstantCompositionExpansionTest:1:",
}

TEST_DATA = {
    "columns": [
        "ConstantCompositionExpansionTestID",
        "TestNumber",
        "FluidSampleID",
        "TestTemperature",
        "SaturationPressure",
        "ReservoirPressure",
        "ConstantCompositionExpansionTestSteps",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--ConstantCompositionExpansionTest:1:",
            "1",
            "opendes:master-data--FluidSample:1:",
            {
                "Value": 1.0,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
            },
            {
                "Value": 1.0,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                "Type": "opendes:reference-data--PressureMeasurementType:1:",
            },
            {
                "Value": 1.0,
                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
            },
            [
                {
                    "StepNumber": "1",
                    "StepPressure": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                        "Type": "opendes:reference-data--PressureMeasurementType:1:",
                    },
                    "LiquidFraction": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "OilDensity": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "OilCompressibility": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "OilViscosity": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "TotalVolume": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "SaturationPressureLiquidVolume": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "IndicatedPressureLiquidVolume": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "RelativeVolumeRatio": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "GasDensity": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "GasZFactor": 1.0,
                    "GasCompressibility": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "GasViscosity": {
                        "Value": 1.0,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:1:",
                    },
                    "YFunction": 1.0,
                    "FluidConditionType": FluidConditionType.Stock_Tank_Conditions.value,
                    "PhasesPresentType": PhasesPresentType.Oil.value,
                },
            ],
        ],
    ],
}

TEST_AGGREGATED_DATA = {
    "columns": [
        "count(\"ConstantCompositionExpansionTestSteps\")",
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
        "ConstantCompositionExpansionTestID",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--ConstantCompositionExpansionTest:1:",
        ],
    ],
}

INCORRECT_SCHEMA_TEST_DATA = {
    "columns": [
        # "id",  # Missing mandatory field
        "WrongField",  # Wrong field
        "data",
        "ConstantCompositionExpansionTestSteps",
    ],
    "index": [0],
    "data": [
        [
            "opendes:work-product-component--CCEMeasurements:1:",
            "opendes:master-data--:1:",  # Incorrect value
            {},
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting DifferentialLiberationTestSteps
EXPECTED_ERROR_REASON = f"Data error: {len(INCORRECT_DATAFRAME_TEST_DATA['columns'])} columns passed, " \
                        f"passed data had {len(INCORRECT_DATAFRAME_TEST_DATA['data'][0])} columns"
