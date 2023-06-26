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

from app.api.routes.data.api import BaseDataView
from app.api.routes.samplesanalysis.api import (
    SAMPLESANALYSIS_ID_REGEX_STR,
    SamplesAnalysisRecordView,
)

RECORD_TYPE = "CapPressure"
BULK_DATASET_PREFIX = "capillary-pressure"

router = APIRouter()
cap_pressure_router = APIRouter()

BaseDataView(
    router=cap_pressure_router,
    id_regex_str=SAMPLESANALYSIS_ID_REGEX_STR,
    bulk_dataset_prefix=BULK_DATASET_PREFIX,
    record_type=RECORD_TYPE,
)

SamplesAnalysisRecordView(
    router=cap_pressure_router,
    record_type=RECORD_TYPE,
)

router.include_router(cap_pressure_router, tags=["capillarypressuretests"], prefix="/capillarypressuretests")
