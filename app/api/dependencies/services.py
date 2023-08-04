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

from fastapi import Depends

from app.api.dependencies.auth import require_authorized_user
from app.api.dependencies.request import (
    get_correlation_id,
    get_data_partition_id,
)
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.models.schemas.user import User
from app.resources.common_headers import CORRELATION_ID
from app.services import dataset, search, storage


async def get_async_dataset_service(
    data_partition_id: str = Depends(get_data_partition_id),
    settings: AppSettings = Depends(get_app_settings),
    user: User = Depends(require_authorized_user),
    correlation_id: str = Depends(get_correlation_id),
):
    return dataset.DatasetService(
        data_partition_id=data_partition_id,
        settings=settings,
        user=user,
        extra_headers={CORRELATION_ID: correlation_id},
    )


async def get_async_storage_service(
    data_partition_id: str = Depends(get_data_partition_id),
    settings: AppSettings = Depends(get_app_settings),
    user: User = Depends(require_authorized_user),
    correlation_id: str = Depends(get_correlation_id),
):
    return storage.StorageService(
        data_partition_id=data_partition_id,
        settings=settings,
        user=user,
        extra_headers={CORRELATION_ID: correlation_id},
    )


async def get_async_search_service(
    data_partition_id: str = Depends(get_data_partition_id),
    settings: AppSettings = Depends(get_app_settings),
    user: User = Depends(require_authorized_user),
    correlation_id: str = Depends(get_correlation_id),
):
    return search.SearchService(
        data_partition_id=data_partition_id,
        settings=settings,
        user=user,
        extra_headers={CORRELATION_ID: correlation_id},
    )
