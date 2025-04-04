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

TEST_DATASET_RECORD_ID = "opendes:dataset--File.Generic:wateranalysisdata-123:1234"
TEST_DDMS_URN = f"urn://rafs-v2/wateranalysisdata/{TEST_SAMPLESANALYSIS_ID}/{TEST_DATASET_RECORD_ID}"
TEST_SCHEMA_VERSION = "1.0.0"
TEST_DDMS_URN_WITH_VERSION = f"urn://rafs-v2/wateranalysisdata/{TEST_SAMPLESANALYSIS_ID}/{TEST_DATASET_RECORD_ID}/{TEST_SCHEMA_VERSION}"
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
    "columns_filter": "SamplesAnalysisID,SampleID,TestNumber,WaterSampleComponent",
    "rows_filter": "SampleID,eq,opendes:master-data--Sample:WaterAnalysis_Sample:",
}

with open(f"{dir_path}/water_analysis_data_orient_split.json") as fp:
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
        "TestNumber",
        "WaterSampleComponent",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:WaterAnalysis_WPC:",
            "opendes:master-data--Sample:WaterAnalysis_Sample:",
            "17. Water Analysis",
            [
                {
                    "Anions": [
                        {
                            "ComponentNameID": "C032-",
                            "Value": 11,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:IonChromatography:"
                        },
                        {
                            "ComponentNameID": "HCO3",
                            "Value": 427,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-OES:"
                        }
                    ],
                    "Cations": [
                        {
                            "ComponentNameID": "Na+",
                            "Value": 89,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-OES:"
                        },
                        {
                            "ComponentNameID": "K+",
                            "Value": 112,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-MS:"
                        }
                    ],
                    "DissolvedMetals": [
                        {
                            "ComponentNameID": "Fe",
                            "Value": 0.198,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-MS:"
                        },
                        {
                            "ComponentNameID": "Sr2+",
                            "Value": 18.1,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:IonChromatography:"
                        }
                    ],
                    "OrganicAcids": [
                        {
                            "ComponentNameID": "Fe",
                            "Value": 0.198,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-OES:"
                        },
                        {
                            "ComponentNameID": "Sr2+",
                            "Value": 18.1,
                            "ElementalMeasurementMethodID": "opendes:reference-data--ElementalMeasurementMethod:ICP-MS:"
                        }
                    ],
                    "IonDifference": 0.22,
                    "MolarConcentration": 0.1,
                    "VolumeConcentration": 0.853,
                    "MassConcentration": 0.176,
                    "EquivalentConcentration": 0.095,
                    "ConcentrationRelativeToDetectableLimits": 0.066
                }
            ],
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
INCORRECT_DATAFRAME_TEST_DATA["data"][0].pop()  # deleting WaterSampleComponent in index row 0
EXPECTED_ERROR_REASON = "Data error: 7 columns passed, passed data had 6 columns"
