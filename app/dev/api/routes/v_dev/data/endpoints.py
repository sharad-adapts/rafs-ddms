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

import uuid

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
    get_blob_storage_service,
)
from app.api.dependencies.validation import get_data_model
from app.api.routes.data.api import BaseDataView
from app.api.routes.utils.api_description_helper import APIDescriptionHelper
from app.api.routes.utils.api_version import get_api_version_from_url
from app.api.routes.utils.ddms_datasets import upsert_parquet_data
from app.api.routes.utils.records import (
    get_family_type_from_url,
    get_id_version,
)
from app.core.config import get_app_settings
from app.core.helpers.cache.coder import ResponseCoder
from app.core.helpers.cache.key_builder import key_builder_using_token
from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.core.settings.app import AppSettings
from app.dev.api.dependencies.validation import (
    validate_multiple_nested_filters,
)
from app.dev.api.routes.utils.ddms_datasets import get_parquet_data
from app.dev.api.routes.utils.records import find_dataset_id_from_type
from app.dev.dataframe.multiple_nested_filter_processor import (
    DFMultipleNestedFilterProcessor,
)
from app.dev.resources.multiple_nested_filters import (
    DFMultipleNestedFilterValidator,
)
from app.exceptions import exceptions
from app.providers.dependencies.blob_storage import (
    Blob,
    BlobMetadata,
    IBlobStorage,
)
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
        self.prepare_api_routes()
        if kwargs:
            self.__dict__.update(kwargs)

    @cache(expire=CACHE_DEFAULT_TTL, coder=ResponseCoder, key_builder=key_builder_using_token)
    async def get_data_dev(
        self,
        request: Request,
        record_id: str,
        analysis_type: str,
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        storage_service: storage.StorageService = Depends(get_async_storage_service),
        blob_storage_service: IBlobStorage = Depends(get_blob_storage_service),
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
        :param dataset_service: dataset service
        :type dataset_service: dataset.DatasetService
        :param storage_service: storage service
        :type storage_service: storage.StorageService
        :param blob_storage_service: blob storage service
        :type blob_storage_service: IBlobService
        :param df_filter: df multiple nested filter validator
        :type df_filter: DFMultipleNestedFilterValidator
        :param content_schema_version: the version used for content
            schema validation
        :type content_schema_version: str
        :return: dataset data
        :rtype: Response
        """
        logger.info(f"Get data for type {analysis_type}")
        settings: AppSettings = get_app_settings()

        if settings.use_blob_storage:
            blob_metadata = BlobMetadata(
                analysis_family=get_family_type_from_url(request.url.path),
                analysis_type=analysis_type,
                version=content_schema_version,
                uuid="unused_uuid",
                content_type=SupportedMimeTypes.PARQUET.mime_type,
            )
            response = await get_parquet_data(
                request=request,
                record_id=record_id,
                blob_metadata=blob_metadata,
                blob_storage_service=blob_storage_service,
                storage_service=storage_service,
                df_filter=df_filter,
            )
        else:
            response = await self._get_data(
                request,
                record_id,
                analysis_type,
                dataset_service,
                storage_service,
                df_filter,
                content_schema_version,
            )
        return response

    async def post_data_dev(
        self,
        request: Request,
        record_id: str,
        analysis_type: str,
        storage_service: storage.StorageService = Depends(get_async_storage_service),
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        blob_storage_service: IBlobStorage = Depends(get_blob_storage_service),
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
        :param blob_storage_service: blob storage service
        :type blob_storage_service: IBlobStorage
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

        settings: AppSettings = get_app_settings()
        analysis_family = get_family_type_from_url(request.url.path)

        parquet_file = await self._get_validated_payload(request, model, storage_service)
        blob_metadata = BlobMetadata(
            analysis_family=analysis_family,
            analysis_type=analysis_type,
            version=content_schema_version,
            uuid=uuid.uuid4(),
            content_type=SupportedMimeTypes.PARQUET,
        )
        blob = Blob(blob_data=parquet_file, blob_metadata=blob_metadata)

        logger.info(f"Post data for type {analysis_type}")

        if settings.use_blob_storage:
            response = await upsert_parquet_data(
                blob,
                record_id,
                blob_storage_service,
                storage_service,
            )
        else:
            response = await self._upsert_dataset(
                request,
                record_id,
                parquet_file,
                analysis_type,
                content_schema_version,
                api_version,
                dataset_service,
                storage_service,
            )
        return response

    def prepare_api_routes(self) -> None:
        """Prepare and add api routes."""
        self._prepare_get_data_route_dev()
        self._prepare_post_data_route_dev()

    async def _get_data(
        self,
        request: Request,
        record_id: str,
        analysis_type: str,
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
        :param analysis_type: analysis type
        :type analysis_type: str
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

        ddms_datasets = record["data"].get("DDMSDatasets", [])
        dataset_id = find_dataset_id_from_type(ddms_datasets, analysis_type, content_schema_version)

        if dataset_id:
            dataset_id, _ = get_id_version(dataset_id)
            logger.debug(f"Retrieving dataset: {dataset_id}")
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
            error_msg = f"No dataset found for test {analysis_type} with version {content_schema_version} in record."
            response = JSONResponse(
                {"message": error_msg, "reason": "Not found."},
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

        self._router.add_api_route(
            path="/{record_id}/data/{analysis_type}",
            endpoint=self.get_data_dev,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            description=self.description_template_get_data,
            dependencies=[
                Depends(validate_record_id),
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
