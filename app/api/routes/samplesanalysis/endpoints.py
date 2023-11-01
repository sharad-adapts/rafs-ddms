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

from typing import Annotated, Dict, List

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.api.dependencies.request import (
    get_content_schema_version,
    validate_json_content_type,
)
from app.api.dependencies.services import get_async_storage_service
from app.api.routes.osdu.storage_records import BaseStorageRecordView
from app.api.routes.utils.api_description_helper import APIDescriptionHelper
from app.models.data_schemas.base import PATH_TO_DATA_MODEL_VERSIONS
from app.models.schemas.osdu_storage import (
    OsduStorageRecord,
    StorageUpsertResponse,
)
from app.resources.load_model_example import load_data_example
from app.services import storage

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

            :param Annotated[List[OsduStorageRecord], Body request_records: request records,
            :param storage.StorageService storage_service: storage service instance,
            :return List[dict]: validated records
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
            for path, versions in PATH_TO_DATA_MODEL_VERSIONS.items()
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
        model_versions = PATH_TO_DATA_MODEL_VERSIONS.get(
            f"/{analysistype}/",
        ) or PATH_TO_DATA_MODEL_VERSIONS.get(f"/data/{analysistype}")
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
