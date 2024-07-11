#  Copyright 2024 ExxonMobil Technology and Engineering Company
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

from app.api.routes.samplesanalysis.api import SAMPLESANALYSIS_ID_REGEX_STR
from app.dev.api.routes.v_dev.data.endpoints import BaseDataViewDev
from app.dev.api.routes.v_dev.samplesanalysis.endpoints import (
    SamplesAnalysisSearchDataView,
)

sa_router = APIRouter()
RECORD_TYPE = "SamplesAnalysis"


BaseDataViewDev(
    router=sa_router,
    id_regex_str=SAMPLESANALYSIS_ID_REGEX_STR,
)

SamplesAnalysisSearchDataView(sa_router)
