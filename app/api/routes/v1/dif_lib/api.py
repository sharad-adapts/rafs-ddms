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

from app.api.dependencies.validation import validate_dif_lib_records_payload
from app.api.routes.data.api import BaseDataView
from app.api.routes.osdu.records_linking import StorageRecordViewWithLinking
from app.models.domain.osdu.WPCPVT100 import PVT

DIF_LIB_ID_REGEX_STR = r"^[\w\-\.]+:work-product-component--DifferentialLiberationTest:[\w\-\.\:\%]+$"
RECORD_TYPE = "DifferentialLiberationTest"

dif_lib_router = APIRouter()

BaseDataView(
    router=dif_lib_router,
    id_regex_str=DIF_LIB_ID_REGEX_STR,
    bulk_dataset_prefix="differential-liberation",
    record_type=RECORD_TYPE,
)

StorageRecordViewWithLinking(
    router=dif_lib_router,
    id_regex_str=DIF_LIB_ID_REGEX_STR,
    validate_records_payload=validate_dif_lib_records_payload,
    record_type=RECORD_TYPE,
    child_id_field="PVTTests",
    parent_id_field="PVTReportID",
    parent_model=PVT,
)
