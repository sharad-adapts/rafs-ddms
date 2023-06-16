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

from typing import Optional

from fastapi import Depends, Path
from fastapi.responses import JSONResponse
from starlette import status

from app.api.dependencies.records import (
    get_async_dataset_service,
    get_async_storage_service,
    get_data_file_sources,
)
from app.api.routes.osdu.storage_records import BaseStorageRecordView
from app.resources.source_renderer import FileSourceRenderer
from app.services import dataset, storage


class SamplesAnalysesReportView(BaseStorageRecordView):
    """Samples Analyses Report View.

    :param BaseStorageRecordView: inherits from BaseStorageRecordView
    :type BaseStorageRecordView: BaseStorageRecordView
    """

    async def get_source_data(
        self,
        record_id: str,
        storage_service: dataset.DatasetService = Depends(get_async_storage_service),
        dataset_service: storage.StorageService = Depends(get_async_dataset_service),
        version: Optional[str] = None,
    ) -> JSONResponse:
        """Get source data from data.Datasets property.

        :param record_id: record id
        :type record_id: str
        :param storage_service: storage service, defaults to Depends(get_async_storage_service)
        :type storage_service: dataset.DatasetService, optional
        :param dataset_service: dataset service, defaults to Depends(get_async_dataset_service)
        :type dataset_service: storage.StorageService, optional
        :param version: version, defaults to None
        :type version: Optional[str], optional
        :return: rendered source data response
        :rtype: JSONResponse
        """
        data_file_sources = await get_data_file_sources(record_id, storage_service, dataset_service, version)
        renderer = FileSourceRenderer(data_file_sources)
        return await renderer.render_source_data()

    def _prepare_api_routes(self) -> None:
        """Extends parent method."""
        super()._prepare_api_routes()
        self._prepare_get_source_data_route()

    def _prepare_get_source_data_route(self) -> None:
        """Add api route for get_source_data."""
        async def validate_record_id(record_id: str = Path(default=..., regex=self._id_regex_str)) -> str:
            """Validate if record id matches regex.

            :param record_id: record id
            :type record_id: str
            :return: record id
            :rtype: str
            """
            return record_id

        self._router.add_api_route(
            path="/{record_id}/source",
            endpoint=self.get_source_data,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(validate_record_id)],
        )
