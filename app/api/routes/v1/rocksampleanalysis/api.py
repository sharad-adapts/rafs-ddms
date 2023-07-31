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

from fastapi import APIRouter

from app.api.dependencies.validation import (
    validate_rocksampleanalysis_records_payload,
)
from app.api.routes.data.api import BaseDataView
from app.api.routes.osdu.storage_records import BaseStorageRecordView

ROCKSAMPLEANALYSIS_ID_REGEX_STR = r"^[\w\-\.]+:work-product-component--RockSampleAnalysis:[\w\-\.\:\%]+$"
RECORD_TYPE = "RockSampleAnalysis"

rca_router = APIRouter()

BaseDataView(
    router=rca_router,
    id_regex_str=ROCKSAMPLEANALYSIS_ID_REGEX_STR,
    bulk_dataset_prefix="routine-core-analysis",
    record_type=RECORD_TYPE,
    specific_route_type="rca/",
)

BaseStorageRecordView(
    router=rca_router,
    id_regex_str=ROCKSAMPLEANALYSIS_ID_REGEX_STR,
    validate_records_payload=validate_rocksampleanalysis_records_payload,
    record_type=RECORD_TYPE,
)
