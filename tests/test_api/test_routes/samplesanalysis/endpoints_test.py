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

from contextlib import contextmanager
from unittest.mock import create_autospec, patch

import pytest
from httpx import AsyncClient
from starlette import status

from app.api.dependencies.parquet import get_parquet_loader
from app.api.dependencies.services import (
    get_async_dataset_service,
    get_async_search_service,
)
from app.dataframe import parquet_loader
from app.main import app
from app.services import dataset, search
from tests.test_api.test_routes import dependencies
from tests.test_api.test_routes.data.data_mock_objects import TEST_HEADERS_JSON
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    SAMPLESANALYSIS_ENDPOINT_PATH,
    TEST_HEADERS,
    TEST_SERVER,
)
from tests.test_api.test_routes.samplesanalysis.samplesanalysis_mock_objects import (
    END_TEST_INDEX,
    START_TEST_INDEX,
    dataset_get_signed_urls_response,
    orient_split_tests,
    parquet_loader_read_parquets_response,
    sa_ids_response,
    search_find_records_response,
)

async_dataset_service_mock = create_autospec(dataset.DatasetService, spec_set=True, instance=True)
async_search_service_mock = create_autospec(search.SearchService, spec_set=True, instance=True)
parquet_loader_mock = create_autospec(parquet_loader.ParquetLoader, spec_set=True, instance=True)


async def mock_get_async_dataset_service():
    yield async_dataset_service_mock


async def mock_get_async_search_service():
    yield async_search_service_mock


async def mock_get_parquet_loader():
    yield parquet_loader_mock

ALL_SAMPLES_ANALYSIS_TYPES = [
    "routinecoreanalysis",
    "constantcompositionexpansion",
    "differentialliberation",
    "transport",
    "multistageseparator",
    "compositionalanalysis",
    "swelling",
    "constantvolumedepletion",
    "wateranalysis",
    "interfacialtension",
    "vaporliquidequilibrium",
    "multiplecontactmiscibility",
    "slimtube",
    "extraction",
    "fractionation",
    "relativepermeability",
    "rockcompressibility",
    "watergasrelativepermeability",
    "capillarypressure",
    "electricalproperties",
    "nmr",
    "multiplesalinitytests",
    "gcmsalkanes",
    "gcmsaromatics",
    "gcmsratios",
    "gaschromatographyanalyses",
    "gascompositionanalyses",
    "isotopes",
    "bulkpyrolysisanalyses",
    "coregamma",
    "uniaxial",
    "gcmsms",
    "cec",
    "triaxial",
    "wettabilityindex",
    "tec",
    "edsmapping",
    "xrf",
    "tensilestrength",
    "xrd",
    "pdp",
    "stocktankoilanalysis",
]


@contextmanager
def services_overrides():
    overrides = {
        get_async_search_service: mock_get_async_search_service,
        get_async_dataset_service: mock_get_async_dataset_service,
        get_parquet_loader: mock_get_parquet_loader,
    }
    with dependencies.DependencyOverrider(app, overrides) as mock_dependencies:
        yield mock_dependencies


@pytest.fixture
def with_patched_services_success():
    """Patch services for success."""
    with patch.object(async_search_service_mock, "find_records", return_value=search_find_records_response):
        with patch.object(async_dataset_service_mock, "get_signed_urls", return_value=dataset_get_signed_urls_response):
            with patch.object(parquet_loader_mock, "read_parquet_files", return_value=parquet_loader_read_parquets_response):
                yield


@pytest.mark.asyncio
async def test_types_route():
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(
            f"{SAMPLESANALYSIS_ENDPOINT_PATH}/analysistypes",
            headers=TEST_HEADERS,
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "analysistype", ALL_SAMPLES_ANALYSIS_TYPES,
)
async def test_content_schemas_route(analysistype):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(
            f"{SAMPLESANALYSIS_ENDPOINT_PATH}/{analysistype}/data/schema",
            headers={**TEST_HEADERS, "Accept": "application/json;version=1.0.0"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "analysistype", ALL_SAMPLES_ANALYSIS_TYPES,
)
async def test_content_schemas_wrong_version(analysistype):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(
            f"{SAMPLESANALYSIS_ENDPOINT_PATH}/{analysistype}/data/schema",
            headers={**TEST_HEADERS, "Accept": "application/json;version=0.0.0"},
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == f"Schema not found for {analysistype} and version 0.0.0"


@pytest.mark.asyncio
async def test_content_schemas_wrong_type():
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(
            f"{SAMPLESANALYSIS_ENDPOINT_PATH}/wrongtype/data/schema",
            headers={**TEST_HEADERS, "Accept": "application/json;version=0.0.0"},
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == "Schema not found for wrongtype and version 0.0.0"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "analysistype", ["nmr"],
)
async def test_search_data_success(
    analysistype,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{SAMPLESANALYSIS_ENDPOINT_PATH}/{analysistype}/search/data",
                headers=TEST_HEADERS_JSON,
            )

    assert len(response.json()["index"]) == END_TEST_INDEX - START_TEST_INDEX
    assert response.json()["data"] == [test["data"][0] for test in orient_split_tests]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "analysistype", ["nmr"],
)
async def test_search_success(
    analysistype,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{SAMPLESANALYSIS_ENDPOINT_PATH}/{analysistype}/search",
                headers=TEST_HEADERS_JSON,
            )

    assert response.json() == sa_ids_response
