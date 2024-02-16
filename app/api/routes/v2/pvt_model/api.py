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

from app.api.dependencies.validation import validate_pvt_model_records_payload
from app.api.routes.osdu.storage_records import BaseStorageRecordView
from app.api.routes.utils.records import parse_kind
from app.api.routes.v2.data.endpoints import BaseDataViewV2
from app.models.domain.osdu.base import PVT_MODEL_KINDS

RECORD_TYPE_STR = f"({'|'.join(PVT_MODEL_KINDS)})"  # noqa: WPS237
SUPPORTED_TYPES = f"({'|'.join([parse_kind(kind)['entity_type'] for kind in PVT_MODEL_KINDS])})"  # noqa: WPS237
PVT_MODEL_ID_REGEX_STR = f"^[\w\-\.]+:{SUPPORTED_TYPES}:[\w\-\.\:\%]+$"  # noqa: W605

pvt_model_router = APIRouter()

BaseStorageRecordView(
    router=pvt_model_router,
    id_regex_str=PVT_MODEL_ID_REGEX_STR,
    validate_records_payload=validate_pvt_model_records_payload,
    record_type=RECORD_TYPE_STR,
)

BaseDataViewV2(
    router=pvt_model_router,
    id_regex_str=PVT_MODEL_ID_REGEX_STR,
)
