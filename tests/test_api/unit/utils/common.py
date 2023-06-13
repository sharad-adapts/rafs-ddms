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

from app.api.routes.utils.records import generate_dataset_urn
from tests.test_api.api_version import API_VERSION

EXPECTED_RECORD_ID = "partition:entity_type:record_id"
TEST_DATA_PARTITION_ID = "partition"
TEST_DDMS_ID = "rafs"
TEST_WPC_TYPE = "RockSampleAnalysis"
TEST_ENTITY_TYPE = "routine-core-analysis"
TEST_ENTITY_ID = "123"
TEST_WPC_TYPE_2 = "ConstantCompositionExpansion"
TEST_ENTITY_TYPE_2 = "constant-composition-expansion"
INVALID_URN = "invalid_urn"


def generate_test_id(
    data_partition_id=TEST_DATA_PARTITION_ID,
    wpc_type=TEST_WPC_TYPE,
):
    return f"{data_partition_id}:work-product-component--{wpc_type}:{wpc_type}_test"


def generate_test_dataset_record_id(
    data_partition_id=TEST_DATA_PARTITION_ID,
    entity_type=TEST_ENTITY_TYPE,
    entity_id=TEST_ENTITY_ID,
):
    return f"{data_partition_id}:dataset--File.Generic:{entity_type}-{entity_id}:1234"


TEST_RECORD_ID = generate_test_id()
TEST_DATASET_RECORD_ID = generate_test_dataset_record_id()
TEST_RECORD_ID_2 = generate_test_id(wpc_type=TEST_WPC_TYPE_2)
TEST_DATASET_RECORD_ID_2 = generate_test_dataset_record_id(entity_type=TEST_ENTITY_TYPE_2)


def generate_test_ddms_urn(
    ddms_id=TEST_DDMS_ID,
    api_version=API_VERSION,
    entity_type=f"{TEST_ENTITY_TYPE}data",
    wpc_id=TEST_RECORD_ID,
    dataset_id=TEST_DATASET_RECORD_ID,
):
    return generate_dataset_urn(ddms_id, api_version, entity_type, wpc_id, dataset_id)


TEST_DDMS_DATASET_URN = generate_test_ddms_urn()
ORIGINAL_DDMS_DATASETS = [TEST_DDMS_DATASET_URN]
TEST_DDMS_DATASET_URN_2 = generate_test_ddms_urn(
    entity_type=f"{TEST_ENTITY_TYPE_2}data",
    wpc_id=TEST_RECORD_ID_2,
    dataset_id=TEST_DATASET_RECORD_ID_2,
)
