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

from typing import Annotated, Dict, List, Tuple

import pandas as pd
from fastapi import APIRouter, Body, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from starlette import status

from app.api.dependencies.parquet import get_parquet_loader
from app.api.dependencies.request import (
    get_content_schema_version,
    validate_bulkdata_content_type,
    validate_json_content_type,
)
from app.api.dependencies.services import (
    get_async_dataset_service,
    get_async_search_service,
    get_async_storage_service,
)
from app.api.dependencies.validation import validate_filters
from app.api.routes.osdu.storage_records import BaseStorageRecordView
from app.api.routes.utils.api_description_helper import APIDescriptionHelper
from app.api.routes.utils.records import get_info_from_urn
from app.core.helpers.cache.coder import ResponseCoder
from app.core.helpers.cache.key_builder import key_builder_using_token
from app.core.helpers.cache.settings import CACHE_DEFAULT_TTL
from app.dataframe.parquet_loader import ParquetLoader
from app.models.data_schemas.base import (
    ALL_PATHS_TO_DATA_MODEL,
    ENDPOINT_PATTERNS,
)
from app.models.domain.osdu.base import SAMPLESANALYSIS_KIND
from app.models.schemas.osdu_storage import (
    OsduStorageRecord,
    StorageUpsertResponse,
)
from app.resources.filters import DataFrameFilterValidator
from app.resources.load_model_example import load_data_example
from app.resources.mime_types import SupportedMimeTypes
from app.resources.paths import SAMPLESANALYSIS_TYPE_MAPPING
from app.services import dataset, search, storage

SAMPLESANALYSIS_ID_REGEX_STR = r"^[\w\-\.]+:work-product-component--SamplesAnalysis:[\w\-\.\:\%]+$"


class SamplesAnalysisRecordView(BaseStorageRecordView):
    def __init__(
        self,
        router: APIRouter,
        validate_records_payload: callable,
        record_type: str,
    ) -> None:
        super().__init__(
            router=router,
            id_regex_str=SAMPLESANALYSIS_ID_REGEX_STR,
            validate_records_payload=validate_records_payload,
            record_type=record_type,
        )

    async def post_records(
        self,
        request: Request,
        request_records: Annotated[List[dict], Body(example=load_data_example("samples_analysis.json"))],
        storage_service: storage.StorageService = Depends(get_async_storage_service),
    ) -> StorageUpsertResponse:
        return await super().post_records(request, request_records, storage_service)

    def _prepare_post_records_route(self) -> None:
        """Add api route for post_records without dependencies."""
        async def validate_request_records(
            request_records: List[OsduStorageRecord],
            storage_service: storage.StorageService = Depends(get_async_storage_service),
        ) -> List[dict]:
            """Validate request records.

            :param request_records: request records
            :type request_records: List[OsduStorageRecord]
            :param storage_service: storage service instance, defaults
                  to Depends(get_async_storage_service)
            :type storage_service: storage.StorageService, optional
            :return: validated records
            :rtype: List[dict]
            """
            return await self._validate_records_payload(request_records, storage_service)

        self._router.add_api_route(
            path="",
            endpoint=self.post_records,
            methods=["POST"],
            status_code=status.HTTP_200_OK,
            response_model=StorageUpsertResponse,
            response_model_by_alias=False,
            description=APIDescriptionHelper.append_manage_roles(
                f"Create or update `{self._record_type}` record(s).",
            ),
            dependencies=[
                Depends(validate_request_records),
                Depends(validate_json_content_type),
            ],
        )


class SamplesAnalysisTypesView:
    def __init__(
        self,
        router: APIRouter,
    ) -> None:
        self._router = router
        self._prepare_types_route()

    async def get_types(self) -> JSONResponse:
        """Get available data types and their supported versions."""
        analysis_types_versions_map = {
            path.strip("/").split("/")[-1]: list(versions.keys())
            for path, versions in ALL_PATHS_TO_DATA_MODEL.items()
        }
        return JSONResponse(content=analysis_types_versions_map)

    def _prepare_types_route(self) -> None:
        """Add API route for getting available data types and versions."""
        self._router.add_api_route(
            path="/analysistypes",
            endpoint=self.get_types,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=Dict[str, list],
            description="Get available types.",
        )


class SamplesAnalysisSchemasView:
    def __init__(
        self,
        router: APIRouter,
    ) -> None:
        self._router = router
        self._prepare_content_schema_route()

    async def get_content_schema(
        self,
        analysistype: str,
        content_schema_version: str = Depends(get_content_schema_version),
    ) -> JSONResponse:
        """Get the schema of the given analysis type and version."""
        model_versions = None
        for pattern in ENDPOINT_PATTERNS:
            model_versions = ALL_PATHS_TO_DATA_MODEL.get(pattern.format(analysistype=analysistype))
            if model_versions:
                break
        if model_versions and (model := model_versions.get(content_schema_version)):  # noqa: WPS332
            return JSONResponse(
                content=model.schema(),
            )
        return JSONResponse(
            {"message": f"Schema not found for {analysistype} and version {content_schema_version}"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    def _prepare_content_schema_route(self) -> None:
        """Add API route for getting content schema."""
        self._router.add_api_route(
            path="/{analysistype}/data/schema",
            endpoint=self.get_content_schema,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            response_model=Dict[str, list],
            description=APIDescriptionHelper.append_joined_roles(
                "Get the (`content schema`) for a given `{analysistype}`. <br><br>\
                Use the `Accept` request header to specify content schema version \
                    (example header `Accept: application/json;version=1.0.0` is supported).",
            ),
        )


class SamplesAnalysisSearchDataView:

    def __init__(
        self,
        router: APIRouter,
        **kwargs,
    ) -> None:
        self._router = router
        self.description_template_search_data = APIDescriptionHelper.append_joined_roles(
            "Get the (`queried`) bulk data from every `{analysis_type}` found in search service. <br><br>\
            Use the `Accept` request header to specify content schema version \
                (example header `Accept: */*;version=1.0.0` is supported).<br><br>\
            The  `columns_filter`, `rows_filter`, and  `columns_aggregation` \
                query parameters can be used to manage data in response.",
        )
        self.description_template_search = APIDescriptionHelper.append_joined_roles(
            "Get the (`samples analysis`) ids list that comply with `{query}` for given`{analysis_type}`. <br><br>\
            Use the `Accept` request header to specify content schema version \
                (example header `Accept: */*;version=1.0.0` is supported).<br><br>\
            The  `columns_filter`, `rows_filter`, and  `columns_aggregation` \
                query parameters can be used to manage data in response.",
        )
        self._prepare_api_routes()
        if kwargs:
            self.__dict__.update(kwargs)

    @cache(expire=CACHE_DEFAULT_TTL, coder=ResponseCoder, key_builder=key_builder_using_token)
    async def get_search_data(
        self,
        request: Request,
        analysis_type: str,
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        search_service: search.SearchService = Depends(get_async_search_service),
        df_filter: DataFrameFilterValidator = Depends(validate_filters),
        content_schema_version: str = Depends(get_content_schema_version),
        parquet_loader: ParquetLoader = Depends(get_parquet_loader),
    ) -> Response:
        """Search Data Endpoint.

        :param request: the request object
        :type request: Request
        :param analysis_type: the analysis type
        :type analysis_type: str
        :param dataset_service: dataset service instance, defaults to
            Depends(get_async_dataset_service)
        :type dataset_service: dataset.DatasetService, optional
        :param search_service: search service instance, defaults to
            Depends(get_async_search_service)
        :type search_service: search.SearchService, optional
        :param df_filter: dataframe filter, defaults to
            Depends(validate_filters)
        :type df_filter: DataFrameFilterValidator, optional
        :param content_schema_version: content schema version, defaults
            to Depends(get_content_schema_version)
        :type content_schema_version: str, optional
        :param parquet_loader: parquet loader instance, defaults to
            Depends(get_parquet_loader)
        :type parquet_loader: ParquetLoader, optional
        :return: Either json or parquet response from concatenated
            dataframes from search result
        :rtype: Response
        """
        data_partition_id = request.headers.get("data-partition-id")
        _, dfs = await self._get_search_data(
            data_partition_id,
            analysis_type,
            dataset_service,
            search_service,
            df_filter,
            content_schema_version,
            parquet_loader,
        )

        mime_type = SupportedMimeTypes.find_by_mime_type(request.headers["content-type"])

        parquets = [df[1] for df in dfs]
        if mime_type == SupportedMimeTypes.PARQUET:
            content_response = pd.concat(parquets, ignore_index=True).to_parquet() if parquets else b""
            response = Response(
                content=content_response,
                media_type=SupportedMimeTypes.PARQUET.mime_type,
            )
        else:
            content_response = pd.concat(parquets, ignore_index=True).to_json(orient="split") if parquets else ""
            response = Response(
                content=content_response,
                media_type=SupportedMimeTypes.JSON.mime_type,
            )

        return response

    @cache(expire=CACHE_DEFAULT_TTL, coder=ResponseCoder, key_builder=key_builder_using_token)
    async def get_search(
        self,
        request: Request,
        analysis_type: str,
        dataset_service: dataset.DatasetService = Depends(get_async_dataset_service),
        search_service: search.SearchService = Depends(get_async_search_service),
        df_filter: DataFrameFilterValidator = Depends(validate_filters),
        content_schema_version: str = Depends(get_content_schema_version),
        parquet_loader: ParquetLoader = Depends(get_parquet_loader),
    ) -> JSONResponse:
        """Search Endpoint.

        :param request: the request object
        :type request: Request
        :param analysis_type: the analysis type
        :type analysis_type: str
        :param dataset_service: dataset service instance, defaults to
            Depends(get_async_dataset_service)
        :type dataset_service: dataset.DatasetService, optional
        :param search_service: search service instance, defaults to
            Depends(get_async_search_service)
        :type search_service: search.SearchService, optional
        :param df_filter: dataframe filter, defaults to
            Depends(validate_filters)
        :type df_filter: DataFrameFilterValidator, optional
        :param content_schema_version: content schema version, defaults
            to Depends(get_content_schema_version)
        :type content_schema_version: str, optional
        :param parquet_loader: parquet loader instance, defaults to
            Depends(get_parquet_loader)
        :type parquet_loader: ParquetLoader, optional
        :return: The list with SamplesAnalysis ids obtained from search
        :rtype: Response
        """
        data_partition_id = request.headers.get("data-partition-id")
        analysis_type_ids, dfs = await self._get_search_data(
            data_partition_id,
            analysis_type,
            dataset_service,
            search_service,
            df_filter,
            content_schema_version,
            parquet_loader,
        )

        result_set = []
        analysis_type_ids = dict(analysis_type_ids)
        for dataset_id, df in dfs:
            if not df.empty:
                result_set.append(analysis_type_ids[dataset_id])
        return JSONResponse(content=result_set)

    def _prepare_api_routes(self) -> None:
        """Prepare and add api routes."""
        self._prepare_get_search_data_route()
        self._prepare_get_search_route()

    async def _get_search_data(
        self,
        data_partition_id: str,
        analysis_type: str,
        dataset_service: dataset.DatasetService,
        search_service: search.SearchService,
        df_filter: DataFrameFilterValidator,
        content_schema_version: str,
        parquet_loader: ParquetLoader,
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Fetches parquet files from a given result list obtained from search
        service."""
        analysis_type_ids = await self._find_analysis_type_ids(
            data_partition_id, analysis_type, content_schema_version, search_service,
        )
        dataset_ids = [result_id[0] for result_id in analysis_type_ids]
        signed_urls_for_datasets = await dataset_service.get_signed_urls(dataset_ids)
        dfs = await parquet_loader.read_parquet_files(signed_urls_for_datasets, df_filter)
        return analysis_type_ids, dfs

    async def _find_analysis_type_ids(
        self,
        data_partition_id: str,
        analysis_type: str,
        target_schema_version: str,
        search_service: search.SearchService,
    ) -> List[Tuple[str, str]]:
        """Performs a query to search service to build a list of tuples
        dataset_id, samples_analysis_id."""
        query = self._build_sampleanalysistype_query(data_partition_id, SAMPLESANALYSIS_TYPE_MAPPING[analysis_type])
        search_response = await search_service.find_records(
            kind=SAMPLESANALYSIS_KIND,
            query=query,
        )
        return self._build_result_ids(search_response, target_schema_version, analysis_type)

    def _verify_target_schema(
        self,
        dataset_id: str,
        analysis_type: str,
        current_schema: str,
        target_schema: str,
    ) -> bool:
        """Verify the dataset matches the correct target schema."""
        schema_match = False
        if current_schema == target_schema:
            schema_match = True

        dataset_type_match = False
        if f":{analysis_type}-" in dataset_id:
            dataset_type_match = True

        return schema_match and dataset_type_match

    def _build_result_ids(  # noqa: CCR001
        self,
        search_response: dict,
        target_schema_version: str,
        analysis_type: str,
    ) -> List[Tuple[str, str]]:
        """Build a list of tuples dataset_id, samples_analysis_id."""
        result_ids = []
        for record in search_response.get("results", []):
            if ddms_datasets := record.get("data", {}).get("DDMSDatasets"):  # noqa: WPS332
                for urn in ddms_datasets:
                    urn_info = get_info_from_urn(urn)
                    if self._verify_target_schema(  # noqa: WPS337
                        dataset_id=urn_info["dataset_id"],
                        analysis_type=analysis_type,
                        current_schema=urn_info["content_schema_version"],
                        target_schema=target_schema_version,
                    ):
                        result_ids.append((urn_info["dataset_id"], urn_info["samples_analysis_id"]))  # noqa: WPS220

        return result_ids

    def _build_sampleanalysistype_query(self, data_partition_id: str, analysis_types: List[str]) -> str:
        """Build a query to be used within search service for
        SamplesAnalysisType."""
        analysis_types = [
            f'"{data_partition_id}:reference-data--SampleAnalysisType:{analysis_type}"'
            for analysis_type in analysis_types
        ]
        analysis_types_str = " OR ".join(analysis_types)
        return f"data.SampleAnalysisTypeIDs:({analysis_types_str})"

    def _prepare_get_search_data_route(self) -> None:
        """Add api route for get_search_data."""

        self._router.add_api_route(
            path="/{analysis_type}/search/data",
            endpoint=self.get_search_data,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            description=self.description_template_search_data,
            dependencies=[
                Depends(validate_bulkdata_content_type),
            ],
        )

    def _prepare_get_search_route(self) -> None:
        """Add api route for get_search."""

        self._router.add_api_route(
            path="/{analysis_type}/search",
            endpoint=self.get_search,
            methods=["GET"],
            status_code=status.HTTP_200_OK,
            description=self.description_template_search,
        )
