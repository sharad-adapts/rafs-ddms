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
    TEST_SAMPLESANALYSIS_ID,
)

dir_path = os.path.dirname(os.path.abspath(__file__))

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:capillarypressuredata-12345:1234"
TEST_DDMS_URN = f"urn://rafs-v2/capillarypressuredata/{TEST_SAMPLESANALYSIS_ID}/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v2/capillarypressuredata/{TEST_SAMPLESANALYSIS_ID}/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
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
    "columns_aggregation": "SampleID,count",
}
TEST_PARAMS_FILTERS = {
    "columns_filter": "SamplesAnalysisID,SampleID,TestData",
    "rows_filter": "SamplesAnalysisID,eq,opendes:work-product-component--SamplesAnalysis:CapillaryPressure_WPC:",
}

with open(f"{dir_path}/cappressure_orient_split.json") as fp:
    TEST_DATA = json.load(fp)

TEST_AGGREGATED_DATA = {
    "columns": [
        "SampleID",
    ],
    "index": [
        "count",
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
        "SampleID",
        "TestData",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:CapillaryPressure_WPC:",
            "opendes:master-data--Sample:CapillaryPressure_Sample:",
            [
                {
                    "FluidSystemType": "opendes:reference-data--FluidSystemType:GasBrine:",
                    "Permeability": {
                        "Value": 52.2,
                        "Type": "opendes:reference-data--PermeabilityMeasurementType:Kair:",
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:md:",
                    },
                    "CapillaryPressureMethod": {
                        "Value": "opendes:reference-data--CapillaryPressureMethod:MercuryInjection:",
                    },
                    "InitialWaterSaturation": {
                        "Value": 0.266,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "InitialGasSaturation": {
                        "Value": 1,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                    },
                    "Temperature": {
                        "Value": 0.456,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:rte:",
                    },
                    "CapillaryPressureMax": {
                        "Value": 0.912,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:rre:",
                    },
                    "CapillaryPressureMin": {
                        "Value": 0.612,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:lre:",
                    },
                    "CapillaryPressureSteps": [
                        {
                            "StepNumber": "1",
                            "CapillaryPressure": {
                                "Value": 2,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "PhaseSaturation": [
                                {
                                    "Value": 0.978,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Mercury:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Mercury:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                                {
                                    "Value": 0.238,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ict:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Air:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Air:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "PhaseInjectedVolume": [
                                {
                                    "Value": 0.568,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:tyt:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:AirFreeWellheadCrude:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:AirFreeWellheadCrude:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Nonwetting:",
                                },
                                {
                                    "Value": 0.276,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ght:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Bayol35:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Bayol35:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "Remark": "Test was successfully executed",
                            "CalculatedProperties": {
                                "PoreThroatRadius": {
                                    "Value": 1,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:lrr:",
                                },
                                "PoreThroatMedianRadius": {
                                    "Value": 0.564,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrr:",
                                },
                                "JFunction": {
                                    "Value": 2,
                                },
                                "GasWaterCapillaryPressure": {
                                    "Value": 0.264,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "GasOilCapillaryPressure": {
                                    "Value": 0.164,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "OilWaterCapillaryPressure": {
                                    "Value": 0.161,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrif:",
                                },
                                "GasWaterFWL": {
                                    "Value": 0.361,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                                "OilWaterFWL": {
                                    "Value": 0.398,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                            },
                            "PoreThroatSizeDistribution": [
                                {
                                    "PoreThroatSize": {
                                        "Value": 0.938,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    },
                                    "CumulativePhaseSaturation": {
                                        "Value": 0.123,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ert:",
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Bayol55:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Bayol55:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                    "PhaseSaturationFrequency": {
                                        "Value": 0.454,
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Brine:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Brine:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                },
                            ],
                        },
                        {
                            "StepNumber": "2",
                            "CapillaryPressure": {
                                "Value": 4,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pfgd:",
                            },
                            "PhaseSaturation": [
                                {
                                    "Value": 0.138,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:dft:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:CarbonDioxide:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:CarbonDioxide:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                                {
                                    "Value": 0.238,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:act:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Carnation:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Carnation:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "PhaseInjectedVolume": [
                                {
                                    "Value": 0.561,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:tyt:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:DeadCrudeOil:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:DeadCrudeOil:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Nonwetting:",
                                },
                                {
                                    "Value": 0.346,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:tre:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:DeadBrine:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:DeadBrine:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "Remark": "Test was successfully executed",
                            "CalculatedProperties": {
                                "PoreThroatRadius": {
                                    "Value": 3,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:lrf:",
                                },
                                "PoreThroatMedianRadius": {
                                    "Value": 0.514,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrr:",
                                },
                                "JFunction": {
                                    "Value": 1,
                                },
                                "GasWaterCapillaryPressure": {
                                    "Value": 0.264,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "GasOilCapillaryPressure": {
                                    "Value": 0.164,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "OilWaterCapillaryPressure": {
                                    "Value": 0.171,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrvf:",
                                },
                                "GasWaterFWL": {
                                    "Value": 0.888,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                                "OilWaterFWL": {
                                    "Value": 0.387,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                            },
                            "PoreThroatSizeDistribution": [
                                {
                                    "PoreThroatSize": {
                                        "Value": 0.121,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    },
                                    "CumulativePhaseSaturation": {
                                        "Value": 0.899,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ert:",
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Bayol535:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Bayol535:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                    "PhaseSaturationFrequency": {
                                        "Value": 0.467,
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Decane:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Decane:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    "FluidSystemType": "opendes:reference-data--FluidSystemType:OilWater:",
                    "Permeability": {
                        "Value": 88.2,
                        "Type": "opendes:reference-data--PermeabilityMeasurementType:Vari:",
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:rtt:",
                    },
                    "CapillaryPressureMethod": {
                        "Value": "opendes:reference-data--CapillaryPressureMethod:TertiaryDrainageTwoPhase:",
                    },
                    "InitialWaterSaturation": {
                        "Value": 0.556,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:jkj:",
                    },
                    "InitialGasSaturation": {
                        "Value": 1,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ffd:",
                    },
                    "Temperature": {
                        "Value": 0.988,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:rte:",
                    },
                    "CapillaryPressureMax": {
                        "Value": 0.433,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:bvb:",
                    },
                    "CapillaryPressureMin": {
                        "Value": 0.612,
                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:lre:",
                    },
                    "CapillaryPressureSteps": [
                        {
                            "StepNumber": "1",
                            "CapillaryPressure": {
                                "Value": 2,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:psia:",
                            },
                            "PhaseSaturation": [
                                {
                                    "Value": 0.978,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:DIWater:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:DIWater:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                                {
                                    "Value": 0.767,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:uyu:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:EquilibriumGas:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:EquilibriumGas:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "PhaseInjectedVolume": [
                                {
                                    "Value": 0.568,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:cccs:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:GasUnspecified:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:GasUnspecified:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Nonwetting:",
                                },
                                {
                                    "Value": 0.544,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ddd:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Helium:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Helium:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "Remark": "Test was successfully executed",
                            "CalculatedProperties": {
                                "PoreThroatRadius": {
                                    "Value": 1,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:lrr:",
                                },
                                "PoreThroatMedianRadius": {
                                    "Value": 0.564,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrr:",
                                },
                                "JFunction": {
                                    "Value": 2,
                                },
                                "GasWaterCapillaryPressure": {
                                    "Value": 0.264,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "GasOilCapillaryPressure": {
                                    "Value": 0.164,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "OilWaterCapillaryPressure": {
                                    "Value": 0.161,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrif:",
                                },
                                "GasWaterFWL": {
                                    "Value": 0.361,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                                "OilWaterFWL": {
                                    "Value": 0.398,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                            },
                            "PoreThroatSizeDistribution": [
                                {
                                    "PoreThroatSize": {
                                        "Value": 0.938,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    },
                                    "CumulativePhaseSaturation": {
                                        "Value": 0.123,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ert:",
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Bayol55:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Bayol55:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                    "PhaseSaturationFrequency": {
                                        "Value": 0.454,
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Brine:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Brine:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                },
                            ],
                        },
                        {
                            "StepNumber": "2",
                            "CapillaryPressure": {
                                "Value": 4,
                                "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pfgd:",
                            },
                            "PhaseSaturation": [
                                {
                                    "Value": 0.138,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:dft:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:LabOil:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:LabOil:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                                {
                                    "Value": 0.238,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:act:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Kerosene:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Kerosene:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "PhaseInjectedVolume": [
                                {
                                    "Value": 0.561,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:tyt:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:IsoparBlend:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:IsoparBlend:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Nonwetting:",
                                },
                                {
                                    "Value": 0.346,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:tre:",
                                    "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Isopar:",
                                    "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Isopar:",
                                    "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                },
                            ],
                            "Remark": "Test was successfully executed",
                            "CalculatedProperties": {
                                "PoreThroatRadius": {
                                    "Value": 3,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:vcv:",
                                },
                                "PoreThroatMedianRadius": {
                                    "Value": 0.514,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrr:",
                                },
                                "JFunction": {
                                    "Value": 1,
                                },
                                "GasWaterCapillaryPressure": {
                                    "Value": 1,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yri:",
                                },
                                "GasOilCapillaryPressure": {
                                    "Value": 0.164,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:dfd:",
                                },
                                "OilWaterCapillaryPressure": {
                                    "Value": 0.665,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:yrvf:",
                                },
                                "GasWaterFWL": {
                                    "Value": 0.888,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:iuu:",
                                },
                                "OilWaterFWL": {
                                    "Value": 0.887,
                                    "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ysi:",
                                },
                            },
                            "PoreThroatSizeDistribution": [
                                {
                                    "PoreThroatSize": {
                                        "Value": 0.121,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:pct:",
                                    },
                                    "CumulativePhaseSaturation": {
                                        "Value": 0.899,
                                        "UnitOfMeasure": "opendes:reference-data--UnitOfMeasure:ert:",
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Hexane:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Hexane:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                    "PhaseSaturationFrequency": {
                                        "Value": 0.467,
                                        "DisplacingFluid": "opendes:reference-data--DisplacingFluidType:Hexadecane:",
                                        "DisplacedFluid": "opendes:reference-data--DisplacedFluidType:Hexadecane:",
                                        "WettabilityPhaseType": "opendes:reference-data--WettabilityPhaseType:Wetting:",
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
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
            "opendes:work-product-component--SamplesAnalysis:cappressure-test:",
            "opendes:master-data--:1:",  # Incorrect master-data value
        ],
    ],
}

INCORRECT_DATAFRAME_TEST_DATA = copy.deepcopy(TEST_DATA)
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting TestData in index row 0
EXPECTED_ERROR_REASON = "Data error: 3 columns passed, passed data had 2 columns"
