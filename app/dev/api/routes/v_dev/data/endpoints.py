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


from fastapi import APIRouter, Depends, Path, Request, Response
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from loguru import logger
from pydantic import BaseModel
from starlette import status

from app.api.dependencies.request import (
    get_content_schema_version,
    validate_bulkdata_content_type,
)
from app.api.dependencies.services import (
    get_async_dataset_service,
    get_async_storage_service,
)
from app.api.dependencies.validation import get_data_model
from app.api.routes.data.api import BaseDataView
from app.api.routes.utils.api_description_helper import APIDescriptionHelper
from app.api.routes.utils.api_version import get_api_version_from_url
from app.api.routes.utils.records import dataset_id_exist, get_id_version
from app.core.helpers.cache.coder import ResponseCoder
from app.core.helpers.cache.key_builder import key_builder_using_token
from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.dev.api.dependencies.validation import (
    validate_multiple_nested_filters,
)
from app.dev.dataframe.multiple_nested_filter_processor import (
    DFMultipleNestedFilterProcessor,
)
from app.dev.resources.multiple_nested_filters import (
    DFMultipleNestedFilterValidator,
)
from app.exceptions import exceptions
from app.resources.mime_types import SupportedMimeTypes
from app.services import dataset, storage


class BaseDataViewDev(BaseDataView):

    def __init__(
        self,
        router: APIRouter,
        id_regex_str: str,
        **kwargs,
    ) -> None:
        self._router = router
        self._id_regex_str = id_regex_str
        self.description_template_post_data = APIDescriptionHelper.append_manage_roles(
            "Upload the bulk data for a given `{analysis_type}` object by record id.<br>\
            It creates a new version of the record. <br>\
            The previous meta-data with bulk data is available by their `versions`. <br> <br>\
            Use the `Content-Type` request header to specify payload and response formats \
                (`application/json` and `application/parquet` are supported).<br>\
            Use the `Accept` request header to specify content schema version \
                (example header `Accept: */*;version=1.0.0` is supported).",
        )
        self.description_template_get_data = APIDescriptionHelper.append_joined_roles(
            "Get the (`latest version`) bulk data for a given `{analysis_type}` object by record id. <br><br>\
            Use the `Accept` request header to specify content schema version \
                (example header `Accept: */*;version=1.0.0` is supported).<br><br>\
            The  `columns_filter`, `rows_filter`, and  `columns_aggregation` \
                query parameters can be used to manage data in response.",
        )
        self.bulk_dataset_regex = r"[\w\-\.]+:dataset--File.Generic:[\w\-\d\.]+:?[\w\-\.\:\%]*"
        self.prepare_api_routes()
        if kwargs:
            self.__dict__.update(kwargs)

    @cache(expire=CACHE_DEFAULT_TTL, coder=ResponseCoder, key_builder=key_builder_using_token)
    async def get_data_dev(
        self,
        request: Request,
        record_id: str,
        analysis_type: str,
        dataset_id: str,
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        storage_service: storage.StorageService = Depends(get_async_storage_service),
        df_filter: DFMultipleNestedFilterValidator = Depends(validate_multiple_nested_filters),
        content_schema_version: str = Depends(get_content_schema_version),
    ) -> Response:
        """Get record data.

        :param request: request
        :type request: Request
        :param record_id: record id,
        :type record_id: str
        :param analysis_type: the samples analysis type
        :type analysis_type: str
        :param dataset_id: dataset id,
        :type dataset_id: str
        :param dataset_service: dataset service
        :type dataset_service: dataset.DatasetService
        :param storage_service: storage service
        :type storage_service: storage.StorageService
        :param df_filter: df multiple nested filter validator
        :type df_filter: DFMultipleNestedFilterValidator
        :param content_schema_version: the version used for content
            schema validation
        :type content_schema_version: str
        :return: dataset data
        :rtype: Response
        """
        logger.info(f"Get data for type {analysis_type}")

        return await self._get_data(
            request,
            record_id,
            dataset_id,
            dataset_service,
            storage_service,
            df_filter,
            content_schema_version,
        )

    async def post_data_dev(
        self,
        request: Request,
        record_id: str,
        analysis_type: str,
        storage_service: storage.StorageService = Depends(get_async_storage_service),
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        model: BaseModel = Depends(get_data_model),
        content_schema_version: str = Depends(get_content_schema_version),
    ) -> dict:
        """Post record data.

        :param request: request
        :type request: Request
        :param record_id: record id
        :type record_id: str
        :param analysis_type: the samples analysis type
        :type analysis_type: str
        :param dataset_id: dataset id,
        :type dataset_id: str
        :param storage_service: storage service
        :type storage_service: storage.StorageService
        :param dataset_service: dataset service
        :type dataset_service: dataset.DatasetService
        :param model: pydantic model for validation
        :type model: BaseModel
        :param content_schema_version: the version used for content
            schema validation
        :type content_schema_version: str
        :raises exceptions.InvalidDatasetException: if data impossible
            to read
        :raises exceptions.DataValidationException: if data does not
            match pydantic model
        :raises exceptions.InvalidDatasetException: if data impossible
            to convert to parquet
        :return: upserted records ids
        :rtype: dict
        """
        api_version = get_api_version_from_url(request.url.path)
        logger.info(f"Post data for api version: {api_version}")

        parquet_file = await self._get_validated_payload(request, model, storage_service)

        logger.info(f"Post data for type {analysis_type}")
        return await self._upsert_dataset(
            request,
            record_id,
            parquet_file,
            analysis_type,
            content_schema_version,
            api_version,
            dataset_service,
            storage_service,
        )

    def prepare_api_routes(self) -> None:
        """Prepare and add api routes."""
        self._prepare_get_data_route_dev()
        self._prepare_post_data_route_dev()

    async def _get_data(
        self,
        request: Request,
        record_id: str,
        dataset_id: str,
        dataset_service: dataset.DatasetService,
        storage_service: storage.StorageService,
        df_filter: DFMultipleNestedFilterValidator,
        content_schema_version: str,
    ) -> Response:
        """Get record data.

        :param request: request
        :type request: Request
        :param record_id: record id,
        :type record_id: str
        :param dataset_id: dataset id,
        :type dataset_id: str
        :param dataset_service: dataset service
        :type dataset_service: dataset.DatasetService
        :param storage_service: storage service
        :type storage_service: storage.StorageService
        :param df_filter: df filter validator
        :type df_filter: DFMultipleNestedFilterValidator
        :param content_schema_version: schema version for content
        :type content_schema_version: str
        :return: dataset data
        :rtype: Response
        """
        record = await storage_service.get_record(record_id)
        mime_type = SupportedMimeTypes.find_by_mime_type(request.headers["content-type"])

        dataset_id, _ = get_id_version(dataset_id)
        ddms_datasets = record["data"].get("DDMSDatasets", [])

        if dataset_id_exist(ddms_datasets, dataset_id):
            logger.debug(f"Retrieving dataset: {dataset_id}")
            self._check_content_schema_version(content_schema_version, ddms_datasets, dataset_id)
            parquet_bytes = await dataset_service.download_file(dataset_id)

            if not parquet_bytes:
                reason = f"{dataset_id} exist in record but without content."
                logger.debug(reason)
                raise exceptions.UnprocessableContentException(
                    detail=reason,
                )

            filter_processor = DFMultipleNestedFilterProcessor(df_filter)
            df = filter_processor.apply_filters_from_bytes(parquet_bytes)
            logger.debug(f"Dataset info: {df.size} elements; {df.columns}")

            if mime_type == SupportedMimeTypes.PARQUET:
                df.astype(str)
                response = Response(content=df.to_parquet(), media_type=SupportedMimeTypes.PARQUET.mime_type)
            else:
                response = Response(
                    content=df.to_json(orient="split"),
                    media_type=SupportedMimeTypes.JSON.mime_type,
                )
        else:
            response = JSONResponse(
                {"message": f"{dataset_id} does not exist in current record.", "reason": "Not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return response

    def _prepare_get_data_route_dev(self) -> None:
        """Add api route for get_data."""
        async def validate_record_id(record_id: str = Path(default=..., pattern=self._id_regex_str)) -> str:
            """Validate if record id matches regex.

            :param record_id: record id
            :type record_id: str
            :return: record id
            :rtype: str
            """
            return record_id

        async def validate_dataset_id(dataset_id: str = Path(default=..., pattern=self.bulk_dataset_regex)) -> str:
            """Validate if dataset id matches regex.

            :param dataset_id: dataset id
            :type dataset_id: str
            :return: dataset id
            :rtype: str
            """
            return dataset_id

        self._router.add_api_route(
            path="/{record_id}/data/{analysis_type}/{dataset_id}",
            endpoint=self.get_data_dev,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            description=self.description_template_get_data,
            dependencies=[
                Depends(validate_record_id),
                Depends(validate_dataset_id),
                Depends(validate_bulkdata_content_type),
            ],
        )

    def _prepare_post_data_route_dev(self) -> None:
        """Add api route for post_data."""
        async def validate_record_id(record_id: str = Path(default=..., pattern=self._id_regex_str)) -> str:
            """Validate if record id matches regex.

            :param record_id: record id
            :type record_id: str
            :return: record id
            :rtype: str
            """
            return record_id

        self._router.add_api_route(
            path="/{record_id}/data/{analysis_type}",
            endpoint=self.post_data_dev,
            methods=["POST"],
            status_code=status.HTTP_200_OK,
            description=self.description_template_post_data,
            dependencies=[
                Depends(validate_record_id),
                Depends(validate_bulkdata_content_type),
            ],
        )
