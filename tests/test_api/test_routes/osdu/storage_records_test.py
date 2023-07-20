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
import copy
from contextlib import contextmanager
from unittest.mock import call, create_autospec, patch

import pytest
from httpx import AsyncClient, HTTPStatusError
from starlette import status

from app.api.dependencies.services import get_async_storage_service
from app.main import app
from app.services.storage import StorageService
from tests.test_api.api_version import API_VERSION
from tests.test_api.test_routes import dependencies
from tests.test_api.test_routes.osdu import storage_mock_objects
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    CAP_PRESSURE_ENDPOINT_PATH,
    CCE_ENDPOINT_PATH,
    CCE_RECORD,
    COMPOSITIONALANALYSIS_ENDPOINT_PATH,
    COMPOSITIONALANALYSIS_RECORD,
    CORING_ENDPOINT_PATH,
    CORING_RECORD,
    CVD_ENDPOINT_PATH,
    CVD_RECORD,
    DIF_LIB_ENDPOINT_PATH,
    DL_RECORD,
    ELECTRICAL_PROPERTIES_ENDPOINT_PATH,
    EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE,
    EXPECTED_200_CREATED_RESPONSE,
    EXPECTED_200_VERSIONS_RESPONSE,
    EXPECTED_400_RESPONSE_ON_INVALID_PARENT_PVT,
    EXPECTED_404_RESPONSE,
    EXPECTED_422_NO_KIND_REASON,
    EXPECTED_422_RESPONSE_ON_MISSING_SAMPLESANALYSESREPORT,
    EXPECTED_422_TYPER_ERROR_LIST,
    EXPECTED_422_WRONG_PATTERN,
    EXTRACTION_ENDPOINT_PATH,
    FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH,
    FRACTIONATION_ENDPOINT_PATH,
    INTERFACIAL_TENSION_ENDPOINT_PATH,
    INTERFACIAL_TENSION_RECORD,
    MCM_ENDPOINT_PATH,
    MCM_RECORD,
    MSS_ENDPOINT_PATH,
    MULTISTAGESEPARATOR_RECORD,
    OSDU_GENERIC_RECORD,
    PHYS_CHEM_ENDPOINT_PATH,
    PVT_ENDPOINT_PATH,
    PVT_QUERY_STORAGE_SERVICE_200_RESPONSE,
    PVT_RECORD,
    PVT_STORAGE_SERVICE_200_RESPONSE,
    RELATIVE_PERMEABILITY_ENDPOINT_PATH,
    ROCK_COMPRESSIBILITY_ENDPOINT_PATH,
    ROCKSAMPLE_ENDPOINT_PATH,
    ROCKSAMPLE_RECORD,
    ROCKSAMPLEANALYSIS_ENDPOINT_PATH,
    ROCKSAMPLEANALYSIS_RECORD,
    SAMPLESANALYSIS_RECORD,
    SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
    SLIMTUBETEST_ENDPOINT_PATH,
    SLIMTUBETEST_RECORD,
    STO_ENDPOINT_PATH,
    STO_RECORD,
    STORAGE_SERVICE_200_RESPONSE,
    STORAGE_SERVICE_200_VERSIONS_RESPONSE,
    SWELLING_ENDPOINT_PATH,
    SWELLING_RECORD,
    TEST_CCE_ID,
    TEST_COMPOSITIONALANALYSIS_ID,
    TEST_CORING_ID,
    TEST_CVD_ID,
    TEST_DL_ID,
    TEST_HEADERS,
    TEST_HEADERS_NO_AUTH,
    TEST_INTERFACIAL_TENSION_ID,
    TEST_MCM_ID,
    TEST_MSS_ID,
    TEST_PVT_ID,
    TEST_ROCKSAMPLE_ID,
    TEST_ROCKSAMPLEANALYSIS_ID,
    TEST_SAMPLESANALYSESREPORT_ID,
    TEST_SAMPLESANALYSIS_ID,
    TEST_SERVER,
    TEST_SLIMTUBETEST_ID,
    TEST_STO_ID,
    TEST_SWELLING_ID,
    TEST_TRANSPORT_ID,
    TEST_VLE_ID,
    TEST_WATERANALYSIS_ID,
    TEST_WRONG_ID,
    TRANSPORT_ENDPOINT_PATH,
    TRANSPORT_RECORD,
    VLE_ENDPOINT_PATH,
    VLE_RECORD,
    WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH,
    WATERANALYSIS_ENDPOINT_PATH,
    WATERANALYSIS_RECORD,
    build_storage_service_response_200,
)

storage_record_service_mock = create_autospec(StorageService, spec_set=True, instance=True)


async def query_records_mock(_):
    record_data = PVT_RECORD.dict(exclude_none=True)
    return {
        "records": [
            record_data,
        ],
        "invalidRecords": [],
        "retryRecords": [],
    }


async def mock_get_async_storage_service():
    yield storage_record_service_mock


@contextmanager
def storage_override():
    overrides = {
        get_async_storage_service: mock_get_async_storage_service,
    }
    with dependencies.DependencyOverrider(app, overrides) as mock_dependencies:
        yield mock_dependencies


@pytest.fixture
def with_patched_storage_raises_404(storage_method):
    """Patch storage to raise 404."""
    class Response(object):
        status_code = status.HTTP_404_NOT_FOUND
        content = b"test reason"
        text = "test txt"

    with patch.object(
        storage_record_service_mock,
        storage_method,
        side_effect=HTTPStatusError("test", response=Response(), request=None),
    ):
        yield


@pytest.fixture
def with_patched_storage_created_200(storage_method, osdu_record):
    """Patch storage to 200 created."""
    with patch.object(
        storage_record_service_mock,
        storage_method,
        return_value=STORAGE_SERVICE_200_RESPONSE,
    ):
        with patch.object(
            storage_record_service_mock,
            "query_records",
            return_value={
                "records": [OSDU_GENERIC_RECORD.dict()],
                "invalidRecords": [],
                "retryRecords": [],
            },
        ):
            yield


@pytest.fixture
def with_patched_storage_pvt_link_200(created_responses: list, get_response: dict):
    """Patch storage to 200 created."""
    with patch.object(
        storage_record_service_mock,
        "upsert_records",
        side_effect=created_responses,
    ):
        with patch.object(storage_record_service_mock, "get_record", return_value=get_response):
            yield


@pytest.fixture
def with_patched_storage_raises_40x(storage_method, api_status_code):
    """Patch storage to raise 40x."""
    class Response(object):
        status_code = api_status_code
        content = b"test reason"
        text = "test txt"

    with patch.object(
        storage_record_service_mock,
        storage_method,
        side_effect=HTTPStatusError("test", response=Response(), request=None),
    ):
        with patch.object(
            storage_record_service_mock,
            "query_records",
            side_effect=HTTPStatusError("test", response=Response(), request=None),
        ):
            yield


@pytest.fixture
def with_patched_storage_get_success_200(storage_method, osdu_record):
    """Patch storage to 200 success."""
    with patch.object(storage_record_service_mock, storage_method, return_value=osdu_record):
        yield


@pytest.fixture
def with_patched_storage_get_versions_success_200(storage_method):
    """Patch storage to 200 success."""
    with patch.object(
        storage_record_service_mock,
        storage_method,
        return_value=STORAGE_SERVICE_200_VERSIONS_RESPONSE,
    ):
        yield


@pytest.fixture
def with_patched_storage_query_pvt_200():
    """Patch storage to return pvt record."""
    with patch.object(
        storage_record_service_mock,
        "query_records",
        return_value=PVT_QUERY_STORAGE_SERVICE_200_RESPONSE,
    ):
        yield


@pytest.fixture
def with_patched_storage_query_pvt_invalid_200():
    """Patch storage to return invalid pvt record."""
    record = copy.deepcopy(PVT_QUERY_STORAGE_SERVICE_200_RESPONSE["records"][0])
    invalid_pvt_tests_value = [test_id for test_id in record["data"]["PVTTests"].values()]
    record["data"]["PVTTests"] = invalid_pvt_tests_value
    return_value = {
        "records": [
            record,
        ],
        "invalidRecords": [],
        "retryRecords": [],
    }
    with patch.object(
        storage_record_service_mock,
        "query_records",
        return_value=return_value,
    ):
        yield


@pytest.fixture()
def with_patched_storage_samplesanalysis_missing_parent():
    """Patch storage to return missing SamplesAnalysesReport record ID."""
    return_value = {
        "records": [],
        "invalidRecords": [TEST_SAMPLESANALYSESREPORT_ID],
        "retryRecords": [],
    }
    with patch.object(
        storage_record_service_mock,
        "query_records",
        return_value=return_value,
    ):
        yield


@pytest.fixture()
def with_patched_storage_samplesanalysis_existing_parent():
    """Patch storage to return existing SamplesAnalysesReport record ID."""
    return_value = {
        "records": [SAMPLESANALYSIS_RECORD],
        "invalidRecords": [],
        "retryRecords": [],
    }
    with patch.object(
        storage_record_service_mock,
        "query_records",
        return_value=return_value,
    ):
        yield


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,record_id", [
        ("get_record", "rocksamples", TEST_ROCKSAMPLE_ID),
        ("get_record", "coringreports", TEST_CORING_ID),
        ("get_record", "pvtreports", TEST_PVT_ID),
        ("get_record", "rocksampleanalyses", TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record", "ccereports", TEST_CCE_ID),
        ("get_record", "difflibreports", TEST_DL_ID),
        ("get_record", "transporttests", TEST_TRANSPORT_ID),
        ("get_record", "compositionalanalysisreports", TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record", "multistageseparatortests", TEST_MSS_ID),
        ("get_record", "swellingtests", TEST_SWELLING_ID),
        ("get_record", "constantvolumedepletiontests", TEST_CVD_ID),
        ("get_record", "wateranalysisreports", TEST_WATERANALYSIS_ID),
        ("get_record", "stocktankoilanalysisreports", TEST_STO_ID),
        ("get_record", "interfacialtensiontests", TEST_INTERFACIAL_TENSION_ID),
        ("get_record", "vaporliquidequilibriumtests", TEST_VLE_ID),
        ("get_record", "multiplecontactmiscibilitytests", TEST_MCM_ID),
        ("get_record", "slimtubetests", TEST_SLIMTUBETEST_ID),
        ("get_record", "samplesanalysesreport", storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID),
        ("get_record", "capillarypressuretests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "relativepermeabilitytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "fractionationtests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "extractiontests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "physicalchemistrytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "electricalproperties", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "rockcompressibilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "watergasrelativepermeabilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "formationresistivityindexes", TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_not_found(storage_method, path, record_id, with_patched_storage_raises_404):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}",
                headers=TEST_HEADERS,
            )
    assert all((response.json().get(k) == v for k, v in EXPECTED_404_RESPONSE.items()))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,record_id", [
        ("get_record", "rocksamples", TEST_ROCKSAMPLE_ID),
        ("get_record", "coringreports", TEST_CORING_ID),
        ("get_record", "pvtreports", TEST_PVT_ID),
        ("get_record", "rocksampleanalyses", TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record", "ccereports", TEST_CCE_ID),
        ("get_record", "difflibreports", TEST_DL_ID),
        ("get_record", "transporttests", TEST_TRANSPORT_ID),
        ("get_record", "compositionalanalysisreports", TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record", "multistageseparatortests", TEST_MSS_ID),
        ("get_record", "swellingtests", TEST_SWELLING_ID),
        ("get_record", "constantvolumedepletiontests", TEST_CVD_ID),
        ("get_record", "wateranalysisreports", TEST_WATERANALYSIS_ID),
        ("get_record", "stocktankoilanalysisreports", TEST_STO_ID),
        ("get_record", "interfacialtensiontests", TEST_INTERFACIAL_TENSION_ID),
        ("get_record", "vaporliquidequilibriumtests", TEST_VLE_ID),
        ("get_record", "multiplecontactmiscibilitytests", TEST_MCM_ID),
        ("get_record", "slimtubetests", TEST_SLIMTUBETEST_ID),
        ("get_record", "samplesanalysesreport", storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID),
        ("get_record", "capillarypressuretests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "relativepermeabilitytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "fractionationtests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "extractiontests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "physicalchemistrytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "electricalproperties", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "rockcompressibilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "watergasrelativepermeabilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record", "formationresistivityindexes", TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_version_not_found(storage_method, path, record_id, with_patched_storage_raises_404):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}/versions/1234",
                headers=TEST_HEADERS,
            )

    assert response.json() == EXPECTED_404_RESPONSE
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,record_id", [
        ("get_record_versions", "rocksamples", TEST_ROCKSAMPLE_ID),
        ("get_record_versions", "coringreports", TEST_CORING_ID),
        ("get_record_versions", "pvtreports", TEST_PVT_ID),
        ("get_record_versions", "rocksampleanalyses", TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record_versions", "ccereports", TEST_CCE_ID),
        ("get_record_versions", "difflibreports", TEST_DL_ID),
        ("get_record_versions", "transporttests", TEST_TRANSPORT_ID),
        ("get_record_versions", "compositionalanalysisreports", TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record_versions", "multistageseparatortests", TEST_MSS_ID),
        ("get_record_versions", "swellingtests", TEST_SWELLING_ID),
        ("get_record_versions", "constantvolumedepletiontests", TEST_CVD_ID),
        ("get_record_versions", "wateranalysisreports", TEST_WATERANALYSIS_ID),
        ("get_record_versions", "stocktankoilanalysisreports", TEST_STO_ID),
        ("get_record_versions", "interfacialtensiontests", TEST_INTERFACIAL_TENSION_ID),
        ("get_record_versions", "vaporliquidequilibriumtests", TEST_VLE_ID),
        ("get_record_versions", "multiplecontactmiscibilitytests", TEST_MCM_ID),
        ("get_record_versions", "slimtubetests", TEST_SLIMTUBETEST_ID),
        ("get_record_versions", "samplesanalysesreport", storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID),
        ("get_record_versions", "capillarypressuretests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "relativepermeabilitytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "fractionationtests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "extractiontests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "physicalchemistrytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "electricalproperties", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "rockcompressibilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "watergasrelativepermeabilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "formationresistivityindexes", TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_versions_not_found(
    storage_method, path, record_id,
    with_patched_storage_raises_404,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}/versions",
                headers=TEST_HEADERS,
            )

    assert response.json() == EXPECTED_404_RESPONSE
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,record_id", [
        ("soft_delete_record", "rocksamples", TEST_ROCKSAMPLE_ID),
        ("soft_delete_record", "coringreports", TEST_CORING_ID),
        ("soft_delete_record", "pvtreports", TEST_PVT_ID),
        ("soft_delete_record", "rocksampleanalyses", TEST_ROCKSAMPLEANALYSIS_ID),
        ("soft_delete_record", "ccereports", TEST_CCE_ID),
        ("soft_delete_record", "difflibreports", TEST_DL_ID),
        ("soft_delete_record", "transporttests", TEST_TRANSPORT_ID),
        ("soft_delete_record", "compositionalanalysisreports", TEST_COMPOSITIONALANALYSIS_ID),
        ("soft_delete_record", "multistageseparatortests", TEST_MSS_ID),
        ("soft_delete_record", "swellingtests", TEST_SWELLING_ID),
        ("soft_delete_record", "constantvolumedepletiontests", TEST_CVD_ID),
        ("soft_delete_record", "wateranalysisreports", TEST_WATERANALYSIS_ID),
        ("soft_delete_record", "stocktankoilanalysisreports", TEST_STO_ID),
        ("soft_delete_record", "interfacialtensiontests", TEST_INTERFACIAL_TENSION_ID),
        ("soft_delete_record", "vaporliquidequilibriumtests", TEST_VLE_ID),
        ("soft_delete_record", "multiplecontactmiscibilitytests", TEST_MCM_ID),
        ("soft_delete_record", "slimtubetests", TEST_SLIMTUBETEST_ID),
        ("soft_delete_record", "samplesanalysesreport", storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID),
        ("soft_delete_record", "capillarypressuretests", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "relativepermeabilitytests", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "fractionationtests", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "extractiontests", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "physicalchemistrytests", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "electricalproperties", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "rockcompressibilities", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "watergasrelativepermeabilities", TEST_SAMPLESANALYSIS_ID),
        ("soft_delete_record", "formationresistivityindexes", TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_delete_record_not_found(
    storage_method, path, record_id,
    with_patched_storage_raises_404,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.delete(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}",
                headers=TEST_HEADERS,
            )

    assert response.json() == EXPECTED_404_RESPONSE
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", [
        ("rocksamples"),
        ("coringreports"),
        ("pvtreports"),
        ("rocksampleanalyses"),
        ("ccereports"),
        ("difflibreports"),
        ("transporttests"),
        ("compositionalanalysisreports"),
        ("multistageseparatortests"),
        ("swellingtests"),
        ("constantvolumedepletiontests"),
        ("wateranalysisreports"),
        ("stocktankoilanalysisreports"),
        ("interfacialtensiontests"),
        ("vaporliquidequilibriumtests"),
        ("multiplecontactmiscibilitytests"),
        ("slimtubetests"),
        ("samplesanalysesreport"),
        ("capillarypressuretests"),
        ("relativepermeabilitytests"),
        ("fractionationtests"),
        ("extractiontests"),
        ("physicalchemistrytests"),
        ("electricalproperties"),
        ("rockcompressibilities"),
        ("watergasrelativepermeabilities"),
        ("formationresistivityindexes"),
    ],
)
async def test_post_record_no_kind(path):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[OSDU_GENERIC_RECORD.dict()],
            )

    response_json = response.json()
    assert response_json["code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert EXPECTED_422_NO_KIND_REASON in response.json()["reason"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", [
        ("rocksamples"),
        ("coringreports"),
        ("pvtreports"),
        ("rocksampleanalyses"),
        ("ccereports"),
        ("difflibreports"),
        ("transporttests"),
        ("compositionalanalysisreports"),
        ("multistageseparatortests"),
        ("swellingtests"),
        ("constantvolumedepletiontests"),
        ("wateranalysisreports"),
        ("stocktankoilanalysisreports"),
        ("interfacialtensiontests"),
        ("vaporliquidequilibriumtests"),
        ("multiplecontactmiscibilitytests"),
        ("slimtubetests"),
        ("samplesanalysesreport"),
        ("capillarypressuretests"),
        ("relativepermeabilitytests"),
        ("fractionationtests"),
        ("extractiontests"),
        ("physicalchemistrytests"),
        ("electricalproperties"),
        ("rockcompressibilities"),
        ("watergasrelativepermeabilities"),
        ("formationresistivityindexes"),
    ],
)
async def test_post_record_invalid_payload_type(path):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(f"/api/os-rafs-ddms/{API_VERSION}/{path}", headers=TEST_HEADERS, json={})

    assert response.json()["code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["errors"][0] == EXPECTED_422_TYPER_ERROR_LIST


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record,field",
    [
        ("rocksamples", ROCKSAMPLE_RECORD, "WellboreID"),
        ("coringreports", CORING_RECORD, "WellboreID"),
        ("pvtreports", PVT_RECORD, "FluidSampleID"),
        ("rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD, "WellboreID"),
        ("ccereports", CCE_RECORD, "FluidSampleID"),
        ("difflibreports", DL_RECORD, "FluidSampleID"),
        ("transporttests", TRANSPORT_RECORD, "FluidSampleID"),
        ("compositionalanalysisreports", COMPOSITIONALANALYSIS_RECORD, "FluidSampleID"),
        ("multistageseparatortests", MULTISTAGESEPARATOR_RECORD, "FluidSampleID"),
        ("swellingtests", SWELLING_RECORD, "FluidSampleID"),
        ("constantvolumedepletiontests", CVD_RECORD, "FluidSampleID"),
        ("wateranalysisreports", WATERANALYSIS_RECORD, "FluidSampleID"),
        ("stocktankoilanalysisreports", STO_RECORD, "FluidSampleID"),
        ("interfacialtensiontests", INTERFACIAL_TENSION_RECORD, "FluidSampleID"),
        ("vaporliquidequilibriumtests", VLE_RECORD, "FluidSampleID"),
        ("multiplecontactmiscibilitytests", MCM_RECORD, "FluidSampleID"),
        ("slimtubetests", SLIMTUBETEST_RECORD, "FluidSampleID"),
        ("samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD, "DocumentTypeID"),
        ("capillarypressuretests", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("relativepermeabilitytests", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("fractionationtests", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("extractiontests", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("physicalchemistrytests", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("electricalproperties", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("rockcompressibilities", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("watergasrelativepermeabilities", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
        ("formationresistivityindexes", SAMPLESANALYSIS_RECORD, "DepthShiftsID"),
    ],
)
async def test_post_record_invalid_field_type(path, osdu_record, field):
    osdu_record_wrong_field_type = osdu_record.dict()
    osdu_record_wrong_field_type.update({"data": {field: "wrong_pattern"}})

    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record_wrong_field_type],
            )

    assert response.json()["code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert field in response.json()["reason"]
    assert all([s in response.json()["reason"] for s in EXPECTED_422_WRONG_PATTERN])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,osdu_record",
    [
        ("upsert_records", "rocksamples", ROCKSAMPLE_RECORD),
        ("upsert_records", "coringreports", CORING_RECORD),
        ("upsert_records", "pvtreports", PVT_RECORD),
        ("upsert_records", "rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD),
        ("upsert_records", "samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD),
    ],
)
async def test_post_record_success(
    storage_method, path, osdu_record,
    with_patched_storage_created_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == EXPECTED_200_CREATED_RESPONSE
    storage_record_service_mock.upsert_records.assert_called_once_with(
        [osdu_record.dict(exclude_none=True)],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record",
    [
        (
            "ccereports",
            CCE_RECORD,
        ),
        (
            "difflibreports",
            DL_RECORD,
        ),
        (
            "transporttests",
            TRANSPORT_RECORD,
        ),
        (
            "compositionalanalysisreports",
            COMPOSITIONALANALYSIS_RECORD,
        ),
        (
            "multistageseparatortests",
            MULTISTAGESEPARATOR_RECORD,
        ),
        (
            "swellingtests",
            SWELLING_RECORD,
        ),
        (
            "constantvolumedepletiontests",
            CVD_RECORD,
        ),
        (
            "wateranalysisreports",
            WATERANALYSIS_RECORD,
        ),
        (
            "stocktankoilanalysisreports",
            STO_RECORD,
        ),
        (
            "interfacialtensiontests",
            INTERFACIAL_TENSION_RECORD,
        ),
        (
            "vaporliquidequilibriumtests",
            VLE_RECORD,
        ),
        (
            "multiplecontactmiscibilitytests",
            MCM_RECORD,
        ),
        (
            "slimtubetests",
            SLIMTUBETEST_RECORD,
        ),
    ],
)
async def test_post_record_with_invalid_pvt_parent(
    path,
    osdu_record,
    with_patched_storage_query_pvt_invalid_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result_json = response.json()
    assert result_json == EXPECTED_400_RESPONSE_ON_INVALID_PARENT_PVT


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record,created_responses,get_response",
    [
        (
            "ccereports",
            CCE_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_CCE_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_CCE_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "difflibreports",
            DL_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_DL_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_DL_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "transporttests",
            TRANSPORT_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_TRANSPORT_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_TRANSPORT_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "compositionalanalysisreports",
            COMPOSITIONALANALYSIS_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_COMPOSITIONALANALYSIS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_COMPOSITIONALANALYSIS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "swellingtests",
            SWELLING_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_SWELLING_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_SWELLING_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "multistageseparatortests",
            MULTISTAGESEPARATOR_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_MSS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_MSS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "constantvolumedepletiontests",
            CVD_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_CVD_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_CVD_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "wateranalysisreports",
            WATERANALYSIS_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_WATERANALYSIS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_WATERANALYSIS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "stocktankoilanalysisreports",
            STO_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_STO_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_STO_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "interfacialtensiontests",
            INTERFACIAL_TENSION_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_INTERFACIAL_TENSION_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_INTERFACIAL_TENSION_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "vaporliquidequilibriumtests",
            VLE_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_VLE_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_VLE_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "multiplecontactmiscibilitytests",
            MCM_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_MCM_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_MCM_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "slimtubetests",
            SLIMTUBETEST_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_SLIMTUBETEST_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_SLIMTUBETEST_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
    ],
)
async def test_post_record_success_update_pvt_parent(
    path,
    osdu_record,
    created_responses,
    get_response,
    with_patched_storage_pvt_link_200,
    with_patched_storage_query_pvt_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )
            result_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result_json["recordCount"] == EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE["recordCount"]
    assert set(result_json["recordIdVersions"]) == {f"{osdu_record.id}:1", f"{osdu_record.data.PVTReportID}1"}
    assert result_json["skippedRecordCount"] == EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE["skippedRecordCount"]
    assert storage_record_service_mock.upsert_records.call_args_list[0] == call([osdu_record.dict(exclude_none=True)])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record",
    [
        (
            "capillarypressuretests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "relativepermeabilitytests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "fractionationtests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "extractiontests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "physicalchemistrytests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "electricalproperties",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "rockcompressibilities",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "watergasrelativepermeabilities",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "formationresistivityindexes",
            SAMPLESANALYSIS_RECORD,
        ),
    ],
)
async def test_post_samplesanalysis_with_missing_parent(
    path,
    osdu_record,
    with_patched_storage_samplesanalysis_missing_parent,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    result_json = response.json()
    assert result_json == EXPECTED_422_RESPONSE_ON_MISSING_SAMPLESANALYSESREPORT


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,osdu_record",
    [
        (
            "upsert_records",
            "capillarypressuretests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "capillarypressuretests",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "relativepermeabilitytests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "relativepermeabilitytests",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "fractionationtests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "fractionationtests",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "physicalchemistrytests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "physicalchemistrytests",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "extractiontests",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "extractiontests",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "electricalproperties",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "rockcompressibilities",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "rockcompressibilities",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "watergasrelativepermeabilities",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "watergasrelativepermeabilities",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
        (
            "upsert_records",
            "formationresistivityindexes",
            SAMPLESANALYSIS_RECORD,
        ),
        (
            "upsert_records",
            "formationresistivityindexes",
            SAMPLESANALYSIS_RECORD_WITHOUT_PARENT,
        ),
    ],
)
async def test_post_samplesanalysis_success(
    storage_method,
    path,
    osdu_record,
    with_patched_storage_created_200,
    with_patched_storage_samplesanalysis_existing_parent,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == EXPECTED_200_CREATED_RESPONSE
    storage_record_service_mock.upsert_records.assert_called_once_with(
        [osdu_record.dict(exclude_none=True)],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,osdu_record",
    [
        ("upsert_records", "rocksamples", ROCKSAMPLE_RECORD),
        ("upsert_records", "coringreports", CORING_RECORD),
        ("upsert_records", "pvtreports", PVT_RECORD),
        ("upsert_records", "rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD),
        ("upsert_records", "samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD),
    ],
)
async def test_post_record_no_id(
    storage_method,
    path,
    osdu_record,
    with_patched_storage_created_200,
):
    osdu_record_json = osdu_record.dict(
        exclude={"id"},
        exclude_none=True,
    )
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record_json],
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == EXPECTED_200_CREATED_RESPONSE
    storage_record_service_mock.upsert_records.assert_called_once_with([osdu_record_json])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record,created_responses,get_response",
    [
        (
            "ccereports",
            CCE_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_CCE_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_CCE_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "difflibreports",
            DL_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_DL_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_DL_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "transporttests",
            TRANSPORT_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_TRANSPORT_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_TRANSPORT_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "compositionalanalysisreports",
            COMPOSITIONALANALYSIS_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_COMPOSITIONALANALYSIS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_COMPOSITIONALANALYSIS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "swellingtests",
            SWELLING_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_SWELLING_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_SWELLING_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "multistageseparatortests",
            MULTISTAGESEPARATOR_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_MSS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_MSS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "constantvolumedepletiontests",
            CVD_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_CVD_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_CVD_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "wateranalysisreports",
            WATERANALYSIS_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_WATERANALYSIS_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_WATERANALYSIS_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "stocktankoilanalysisreports",
            STO_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_STO_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_STO_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "interfacialtensiontests",
            INTERFACIAL_TENSION_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_INTERFACIAL_TENSION_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_INTERFACIAL_TENSION_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "vaporliquidequilibriumtests",
            VLE_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_VLE_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_VLE_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "multiplecontactmiscibilitytests",
            MCM_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_MCM_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_MCM_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
        (
            "slimtubetests",
            SLIMTUBETEST_RECORD,
            [
                build_storage_service_response_200(
                    record_count=1,
                    record_ids=[TEST_SLIMTUBETEST_ID],
                    skipped_record_ids=[],
                    record_id_versions=[f"{TEST_SLIMTUBETEST_ID}:1"],
                ),
                PVT_STORAGE_SERVICE_200_RESPONSE,
            ],
            PVT_RECORD.dict(exclude_none=True),
        ),
    ],
)
async def test_post_record_with_linking_no_id(
    path,
    osdu_record,
    created_responses,
    get_response,
    with_patched_storage_pvt_link_200,
    with_patched_storage_query_pvt_200,
):
    osdu_record_json = osdu_record.dict(
        exclude={"id"},
        exclude_none=True,
    )
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record_json],
            )
            result_json = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result_json["recordCount"] == EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE["recordCount"]
    assert set(result_json["recordIdVersions"]) == {f"{osdu_record.id}:1", f"{osdu_record.data.PVTReportID}1"}
    assert result_json["skippedRecordCount"] == EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE["skippedRecordCount"]
    assert storage_record_service_mock.upsert_records.call_args_list[0] == call([osdu_record_json])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,osdu_record,record_id",
    [
        ("get_record", "rocksamples", ROCKSAMPLE_RECORD, TEST_ROCKSAMPLE_ID),
        ("get_record", "coringreports", CORING_RECORD, TEST_CORING_ID),
        ("get_record", "pvtreports", PVT_RECORD, TEST_PVT_ID),
        ("get_record", "rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD, TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record", "ccereports", CCE_RECORD, TEST_CCE_ID),
        ("get_record", "difflibreports", DL_RECORD, TEST_DL_ID),
        ("get_record", "transporttests", TRANSPORT_RECORD, TEST_TRANSPORT_ID),
        ("get_record", "compositionalanalysisreports", COMPOSITIONALANALYSIS_RECORD, TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record", "multistageseparatortests", MULTISTAGESEPARATOR_RECORD, TEST_MSS_ID),
        ("get_record", "swellingtests", SWELLING_RECORD, TEST_SWELLING_ID),
        ("get_record", "constantvolumedepletiontests", CVD_RECORD, TEST_CVD_ID),
        ("get_record", "wateranalysisreports", WATERANALYSIS_RECORD, TEST_WATERANALYSIS_ID),
        ("get_record", "stocktankoilanalysisreports", STO_RECORD, TEST_STO_ID),
        ("get_record", "interfacialtensiontests", INTERFACIAL_TENSION_RECORD, TEST_INTERFACIAL_TENSION_ID),
        ("get_record", "vaporliquidequilibriumtests", VLE_RECORD, TEST_VLE_ID),
        ("get_record", "multiplecontactmiscibilitytests", MCM_RECORD, TEST_MCM_ID),
        ("get_record", "slimtubetests", SLIMTUBETEST_RECORD, TEST_SLIMTUBETEST_ID),
        (
            "get_record", "samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD,
            storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID,
        ),
        ("get_record", "capillarypressuretests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "relativepermeabilitytests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "fractionationtests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "extractiontests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "physicalchemistrytests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "electricalproperties", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "rockcompressibilities", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "watergasrelativepermeabilities", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "formationresistivityindexes", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_success(
    storage_method, path, osdu_record, record_id,
    with_patched_storage_get_success_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}", headers=TEST_HEADERS)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == osdu_record.dict()
    storage_record_service_mock.get_record.assert_called_once_with(record_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,osdu_record,record_id",
    [
        ("get_record", "rocksamples", ROCKSAMPLE_RECORD, TEST_ROCKSAMPLE_ID),
        ("get_record", "coringreports", CORING_RECORD, TEST_CORING_ID),
        ("get_record", "pvtreports", PVT_RECORD, TEST_PVT_ID),
        ("get_record", "rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD, TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record", "ccereports", CCE_RECORD, TEST_CCE_ID),
        ("get_record", "difflibreports", DL_RECORD, TEST_DL_ID),
        ("get_record", "transporttests", TRANSPORT_RECORD, TEST_TRANSPORT_ID),
        ("get_record", "compositionalanalysisreports", COMPOSITIONALANALYSIS_RECORD, TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record", "multistageseparatortests", MULTISTAGESEPARATOR_RECORD, TEST_MSS_ID),
        ("get_record", "swellingtests", SWELLING_RECORD, TEST_SWELLING_ID),
        ("get_record", "constantvolumedepletiontests", CVD_RECORD, TEST_CVD_ID),
        ("get_record", "wateranalysisreports", WATERANALYSIS_RECORD, TEST_WATERANALYSIS_ID),
        ("get_record", "stocktankoilanalysisreports", STO_RECORD, TEST_STO_ID),
        ("get_record", "interfacialtensiontests", INTERFACIAL_TENSION_RECORD, TEST_INTERFACIAL_TENSION_ID),
        ("get_record", "vaporliquidequilibriumtests", VLE_RECORD, TEST_VLE_ID),
        ("get_record", "multiplecontactmiscibilitytests", MCM_RECORD, TEST_MCM_ID),
        ("get_record", "slimtubetests", SLIMTUBETEST_RECORD, TEST_SLIMTUBETEST_ID),
        (
            "get_record", "samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD,
            storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID,
        ),
        ("get_record", "capillarypressuretests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "relativepermeabilitytests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "fractionationtests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "extractiontests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "physicalchemistrytests", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "electricalproperties", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "rockcompressibilities", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "watergasrelativepermeabilities", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
        ("get_record", "formationresistivityindexes", SAMPLESANALYSIS_RECORD, TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_version_success(
    storage_method, path, osdu_record, record_id,
    with_patched_storage_get_success_200,
):
    with storage_override():
        test_version = 1234
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}/versions/{test_version}", headers=TEST_HEADERS,
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == osdu_record.dict()
    storage_record_service_mock.get_record.assert_called_once_with(record_id, test_version)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,path,record_id", [
        ("get_record_versions", "rocksamples", TEST_ROCKSAMPLE_ID),
        ("get_record_versions", "coringreports", TEST_CORING_ID),
        ("get_record_versions", "pvtreports", TEST_PVT_ID),
        ("get_record_versions", "rocksampleanalyses", TEST_ROCKSAMPLEANALYSIS_ID),
        ("get_record_versions", "ccereports", TEST_CCE_ID),
        ("get_record_versions", "difflibreports", TEST_DL_ID),
        ("get_record_versions", "transporttests", TEST_TRANSPORT_ID),
        ("get_record_versions", "compositionalanalysisreports", TEST_COMPOSITIONALANALYSIS_ID),
        ("get_record_versions", "multistageseparatortests", TEST_MSS_ID),
        ("get_record_versions", "swellingtests", TEST_SWELLING_ID),
        ("get_record_versions", "constantvolumedepletiontests", TEST_CVD_ID),
        ("get_record_versions", "wateranalysisreports", TEST_WATERANALYSIS_ID),
        ("get_record_versions", "stocktankoilanalysisreports", TEST_STO_ID),
        ("get_record_versions", "interfacialtensiontests", TEST_INTERFACIAL_TENSION_ID),
        ("get_record_versions", "vaporliquidequilibriumtests", TEST_VLE_ID),
        ("get_record_versions", "multiplecontactmiscibilitytests", TEST_MCM_ID),
        ("get_record_versions", "slimtubetests", TEST_SLIMTUBETEST_ID),
        ("get_record_versions", "samplesanalysesreport", storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID),
        ("get_record_versions", "capillarypressuretests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "relativepermeabilitytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "fractionationtests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "physicalchemistrytests", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "electricalproperties", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "rockcompressibilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "watergasrelativepermeabilities", TEST_SAMPLESANALYSIS_ID),
        ("get_record_versions", "formationresistivityindexes", TEST_SAMPLESANALYSIS_ID),
    ],
)
async def test_get_record_versions_success(
    storage_method, path, record_id,
    with_patched_storage_get_versions_success_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(f"/api/os-rafs-ddms/{API_VERSION}/{path}/{record_id}/versions", headers=TEST_HEADERS)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == EXPECTED_200_VERSIONS_RESPONSE
    storage_record_service_mock.get_record_versions.assert_called_once_with(record_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,api_status_code,path", [
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"rocksamples/{TEST_ROCKSAMPLE_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"coringreports/{TEST_CORING_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"pvtreports/{TEST_PVT_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"rocksampleanalyses/{TEST_ROCKSAMPLEANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"ccereports/{TEST_CCE_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"difflibreports/{TEST_DL_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"transporttests/{TEST_TRANSPORT_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"compositionalanalysisreports/{TEST_COMPOSITIONALANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"multistageseparatortests/{TEST_MSS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"swellingtests/{TEST_SWELLING_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"constantvolumedepletiontests/{TEST_CVD_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"wateranalysisreports/{TEST_WATERANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"stocktankoilanalysisreports/{TEST_STO_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"interfacialtensiontests/{TEST_INTERFACIAL_TENSION_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"vaporliquidequilibriumtests/{TEST_VLE_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"multiplecontactmiscibilitytests/{TEST_MCM_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"slimtubetests/{TEST_SLIMTUBETEST_ID}"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"samplesanalysesreport/{storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID}",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"capillarypressuretests/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"relativepermeabilitytests/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"fractionationtests/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"extractiontests/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"physicalchemistrytests/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"electricalproperties/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"rockcompressibilities/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"watergasrelativepermeabilities/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"formationresistivityindexes/{TEST_SAMPLESANALYSIS_ID}"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"rocksamples/{TEST_ROCKSAMPLE_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"coringreports/{TEST_CORING_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"pvtreports/{TEST_PVT_ID}/versions/1234"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"rocksampleanalyses/{TEST_ROCKSAMPLEANALYSIS_ID}/versions/1234",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"ccereports/{TEST_CCE_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"difflibreports/{TEST_DL_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"transporttests/{TEST_TRANSPORT_ID}/versions/1234"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"compositionalanalysisreports/{TEST_COMPOSITIONALANALYSIS_ID}/versions/1234",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"multistageseparatortests/{TEST_MSS_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"swellingtests/{TEST_SWELLING_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"constantvolumedepletiontests/{TEST_CVD_ID}/versions/1234"),
        (
            "get_record",
            status.HTTP_401_UNAUTHORIZED,
            f"wateranalysisreports/{TEST_WATERANALYSIS_ID}/versions/1234",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"stocktankoilanalysisreports/{TEST_STO_ID}/versions/1234"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"interfacialtensiontests/{TEST_INTERFACIAL_TENSION_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"vaporliquidequilibriumtests/{TEST_VLE_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"multiplecontactmiscibilitytests/{TEST_MCM_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"slimtubetests/{TEST_SLIMTUBETEST_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"samplesanalysesreport/{storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"capillarypressuretests/{TEST_SAMPLESANALYSIS_ID}/versions/1234",
        ),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"relativepermeabilitytests/{TEST_SAMPLESANALYSIS_ID}/versions/1234",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"fractionationtests/{TEST_SAMPLESANALYSIS_ID}/versions/1234"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"extractiontests/{TEST_SAMPLESANALYSIS_ID}/versions/1234",
        ),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"physicalchemistrytests/{TEST_SAMPLESANALYSIS_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"electricalproperties/{TEST_SAMPLESANALYSIS_ID}/versions/1234"),
        ("get_record", status.HTTP_401_UNAUTHORIZED, f"rockcompressibilities/{TEST_SAMPLESANALYSIS_ID}/versions/1234"),
        (
            "get_record", status.HTTP_401_UNAUTHORIZED,
            f"watergasrelativepermeabilities/{TEST_SAMPLESANALYSIS_ID}/versions/1234",
        ),
        (
            "get_record",
            status.HTTP_401_UNAUTHORIZED,
            f"formationresistivityindexes/{TEST_SAMPLESANALYSIS_ID}/versions/1234",
        ),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"rocksamples/{TEST_ROCKSAMPLE_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"coringreports/{TEST_CORING_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"pvtreports/{TEST_PVT_ID}/versions"),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"rocksampleanalyses/{TEST_ROCKSAMPLEANALYSIS_ID}/versions",
        ),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"ccereports/{TEST_CCE_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"difflibreports/{TEST_DL_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"transporttests/{TEST_TRANSPORT_ID}/versions"),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"compositionalanalysisreports/{TEST_COMPOSITIONALANALYSIS_ID}/versions",
        ),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"multistageseparatortests/{TEST_MSS_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"swellingtests/{TEST_SWELLING_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"constantvolumedepletiontests/{TEST_CVD_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"wateranalysisreports/{TEST_WATERANALYSIS_ID}/versions"),
        ("get_record_versions", status.HTTP_401_UNAUTHORIZED, f"stocktankoilanalysisreports/{TEST_STO_ID}/versions"),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"interfacialtensiontests/{TEST_INTERFACIAL_TENSION_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"vaporliquidequilibriumtests/{TEST_VLE_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"multiplecontactmiscibilitytests/{TEST_MCM_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"slimtubetests/{TEST_SLIMTUBETEST_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"samplesanalysesreport/{storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"capillarypressuretests/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"relativepermeabilitytests/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"fractionationtests/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"extractiontests/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"physicalchemistrytests/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"electricalproperties/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"rockcompressibilities/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"watergasrelativepermeabilities/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
        (
            "get_record_versions", status.HTTP_401_UNAUTHORIZED,
            f"formationresistivityindexes/{TEST_SAMPLESANALYSIS_ID}/versions",
        ),
    ],
)
async def test_get_record_auth_errors_from_storage(
    storage_method, api_status_code, path,
    with_patched_storage_raises_40x,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(f"/api/os-rafs-ddms/{API_VERSION}/{path}", headers=TEST_HEADERS)

    assert response.status_code == api_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", [
        ("rocksamples/record_id"),
        ("coringreports/record_id"),
        ("pvtreports/record_id"),
        ("rocksampleanalyses/record_id"),
        ("ccereports/record_id"),
        ("difflibreports/record_id"),
        ("transporttests/record_id"),
        ("compositionalanalysisreports/record_id"),
        ("multistageseparatortests/record_id"),
        ("swellingtests/record_id"),
        ("constantvolumedepletiontests/record_id"),
        ("wateranalysisreports/record_id"),
        ("stocktankoilanalysisreports/record_id"),
        ("interfacialtensiontests/record_id"),
        ("vaporliquidequilibriumtests/record_id"),
        ("multiplecontactmiscibilitytests/record_id"),
        ("slimtubetests/record_id"),
        ("samplesanalysesreport/record_id"),
        ("capillarypressuretests/record_id"),
        ("relativepermeabilitytests/record_id"),
        ("fractionationtests/record_id"),
        ("extractiontests/record_id"),
        ("physicalchemistrytests/record_id"),
        ("electricalproperties/record_id"),
        ("rockcompressibilities/record_id"),
        ("watergasrelativepermeabilities/record_id"),
        ("formationresistivityindexes/record_id"),
        ("rocksamples/record_id/versions/1234"),
        ("coringreports/record_id/versions/1234"),
        ("pvtreports/record_id/versions/1234"),
        ("rocksampleanalyses/record_id/versions/1234"),
        ("ccereports/record_id/versions/1234"),
        ("difflibreports/record_id/versions/1234"),
        ("transporttests/record_id/versions/1234"),
        ("compositionalanalysisreports/record_id/versions/1234"),
        ("multistageseparatortests/record_id/versions/1234"),
        ("swellingtests/record_id/versions/1234"),
        ("constantvolumedepletiontests/record_id/versions/1234"),
        ("wateranalysisreports/record_id/versions/1234"),
        ("stocktankoilanalysisreports/record_id/versions/1234"),
        ("interfacialtensiontests/record_id/versions/1234"),
        ("vaporliquidequilibriumtests/record_id/versions/1234"),
        ("multiplecontactmiscibilitytests/record_id/versions/1234"),
        ("slimtubetests/record_id/versions/1234"),
        ("samplesanalysesreport/record_id/versions/1234"),
        ("capillarypressuretests/record_id/versions/1234"),
        ("relativepermeabilitytests/record_id/versions/1234"),
        ("fractionationtests/record_id/versions/1234"),
        ("extractiontests/record_id/versions/1234"),
        ("physicalchemistrytests/record_id/versions/1234"),
        ("electricalproperties/record_id/versions/1234"),
        ("rockcompressibilities/record_id/versions/1234"),
        ("watergasrelativepermeabilities/record_id/versions/1234"),
        ("formationresistivityindexes/record_id/versions/1234"),
        ("rocksamples/record_id/versions"),
        ("coringreports/record_id/versions"),
        ("pvtreports/record_id/versions"),
        ("rocksampleanalyses/record_id/versions"),
        ("ccereports/record_id/versions"),
        ("difflibreports/record_id/versions"),
        ("transporttests/record_id/versions"),
        ("compositionalanalysisreports/record_id/versions"),
        ("multistageseparatortests/record_id/versions"),
        ("swellingtests/record_id/versions"),
        ("constantvolumedepletiontests/record_id/versions"),
        ("wateranalysisreports/record_id/versions"),
        ("stocktankoilanalysisreports/record_id/versions"),
        ("interfacialtensiontests/record_id/versions"),
        ("vaporliquidequilibriumtests/record_id/versions"),
        ("multiplecontactmiscibilitytests/record_id/versions"),
        ("slimtubetests/record_id/versions"),
        ("samplesanalysesreport/record_id/versions"),
        ("capillarypressuretests/record_id/versions"),
        ("relativepermeabilitytests/record_id/versions"),
        ("fractionationtests/record_id/versions"),
        ("extractiontests/record_id/versions"),
        ("physicalchemistrytests/record_id/versions"),
        ("electricalproperties/record_id/versions"),
        ("rockcompressibilities/record_id/versions"),
        ("watergasrelativepermeabilities/record_id/versions"),
        ("formationresistivityindexes/record_id/versions"),
    ],
)
async def test_get_record_auth_errors(
    path,
):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(f"/api/os-rafs-ddms/{API_VERSION}/{path}", headers=TEST_HEADERS_NO_AUTH)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,api_status_code,path", [
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"rocksamples/{TEST_ROCKSAMPLE_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"coringreports/{TEST_CORING_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"pvtreports/{TEST_PVT_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"rocksampleanalyses/{TEST_ROCKSAMPLEANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"ccereports/{TEST_CCE_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"difflibreports/{TEST_DL_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"transporttests/{TEST_TRANSPORT_ID}"),
        (
            "soft_delete_record",
            status.HTTP_401_UNAUTHORIZED,
            f"compositionalanalysisreports/{TEST_COMPOSITIONALANALYSIS_ID}",
        ),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"multistageseparatortests/{TEST_MSS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"swellingtests/{TEST_SWELLING_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"constantvolumedepletiontests/{TEST_CVD_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"wateranalysisreports/{TEST_WATERANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"stocktankoilanalysisreports/{TEST_STO_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"interfacialtensiontests/{TEST_INTERFACIAL_TENSION_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"vaporliquidequilibriumtests/{TEST_VLE_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"multiplecontactmiscibilitytests/{TEST_MCM_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"slimtubetests/{TEST_SLIMTUBETEST_ID}"),
        (
            "soft_delete_record", status.HTTP_401_UNAUTHORIZED,
            f"samplesanalysesreport/{storage_mock_objects.TEST_SAMPLESANALYSESREPORT_ID}",
        ),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"capillarypressuretests/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"relativepermeabilitytests/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"fractionationtests/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"extractiontests/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"physicalchemistrytests/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"electricalproperties/{TEST_SAMPLESANALYSIS_ID}"),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"rockcompressibilities/{TEST_SAMPLESANALYSIS_ID}"),
        (
            "soft_delete_record", status.HTTP_401_UNAUTHORIZED,
            f"watergasrelativepermeabilities/{TEST_SAMPLESANALYSIS_ID}",
        ),
        ("soft_delete_record", status.HTTP_401_UNAUTHORIZED, f"formationresistivityindexes/{TEST_SAMPLESANALYSIS_ID}"),
    ],
)
async def test_delete_record_auth_errors_from_storage(
    storage_method, api_status_code, path,
    with_patched_storage_raises_40x,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.delete(f"/api/os-rafs-ddms/{API_VERSION}/{path}", headers=TEST_HEADERS)

    assert response.status_code == api_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", [
        ("rocksamples/record_id"),
        ("coringreports/record_id"),
        ("pvtreports/record_id"),
        ("rocksampleanalyses/record_id"),
        ("ccereports/record_id"),
        ("difflibreports/record_id"),
        ("transporttests/record_id"),
        ("compositionalanalysisreports/record_id"),
        ("multistageseparatortests/record_id"),
        ("swellingtests/record_id"),
        ("constantvolumedepletiontests/record_id"),
        ("wateranalysisreports/record_id"),
        ("stocktankoilanalysisreports/record_id"),
        ("interfacialtensiontests/record_id"),
        ("vaporliquidequilibriumtests/record_id"),
        ("multiplecontactmiscibilitytests/record_id"),
        ("slimtubetests/record_id"),
        ("samplesanalysesreport/record_id"),
        ("capillarypressuretests/record_id"),
        ("relativepermeabilitytests/record_id"),
        ("fractionationtests/record_id"),
        ("extractiontests/record_id"),
        ("physicalchemistrytests/record_id"),
        ("electricalproperties/record_id"),
        ("rockcompressibilities/record_id"),
        ("watergasrelativepermeabilities/record_id"),
        ("formationresistivityindexes/record_id"),
    ],
)
async def test_delete_record_auth_errors(
    path,
):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.delete(f"/api/os-rafs-ddms/{API_VERSION}/{path}", headers=TEST_HEADERS_NO_AUTH)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "storage_method,api_status_code,path,osdu_record",
    [
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "rocksamples", ROCKSAMPLE_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "coringreports", CORING_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "pvtreports", PVT_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "ccereports", CCE_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "difflibreports", DL_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "transporttests", TRANSPORT_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "compositionalanalysisreports", COMPOSITIONALANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "constantvolumedepletiontests", CVD_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "multistageseparatortests", MULTISTAGESEPARATOR_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "swellingtests", SWELLING_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "constantvolumedepletiontests", CVD_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "wateranalysisreports", WATERANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "stocktankoilanalysisreports", STO_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "interfacialtensiontests", INTERFACIAL_TENSION_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "vaporliquidequilibriumtests", VLE_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "multiplecontactmiscibilitytests", MCM_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "slimtubetests", SLIMTUBETEST_RECORD),
        (
            "upsert_records", status.HTTP_401_UNAUTHORIZED, "samplesanalysesreport",
            storage_mock_objects.SAMPLESANALYSESREPORT_RECORD,
        ),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "capillarypressuretests", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "relativepermeabilitytests", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "fractionationtests", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "physicalchemistrytests", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "electricalproperties", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "rockcompressibilities", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "watergasrelativepermeabilities", SAMPLESANALYSIS_RECORD),
        ("upsert_records", status.HTTP_401_UNAUTHORIZED, "formationresistivityindexes", SAMPLESANALYSIS_RECORD),
    ],
)
async def test_post_record_auth_errors_from_storage(
    storage_method, api_status_code, path, osdu_record,
    with_patched_storage_raises_40x,
    with_patched_storage_query_pvt_200,
):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                f"/api/os-rafs-ddms/{API_VERSION}/{path}",
                headers=TEST_HEADERS,
                json=[osdu_record.dict(exclude_none=True)],
            )

    assert response.status_code == api_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,osdu_record",
    [
        ("rocksamples", ROCKSAMPLE_RECORD),
        ("coringreports", CORING_RECORD),
        ("pvtreports", PVT_RECORD),
        ("rocksampleanalyses", ROCKSAMPLEANALYSIS_RECORD),
        ("ccereports", CCE_RECORD),
        ("difflibreports", DL_RECORD),
        ("transporttests", TRANSPORT_RECORD),
        ("compositionalanalysisreports", COMPOSITIONALANALYSIS_RECORD),
        ("multistageseparatortests", MULTISTAGESEPARATOR_RECORD),
        ("swellingtests", SWELLING_RECORD),
        ("constantvolumedepletiontests", CVD_RECORD),
        ("wateranalysisreports", WATERANALYSIS_RECORD),
        ("stocktankoilanalysisreports", STO_RECORD),
        ("interfacialtensiontests", INTERFACIAL_TENSION_RECORD),
        ("vaporliquidequilibriumtests", VLE_RECORD),
        ("multiplecontactmiscibilitytests", MCM_RECORD),
        ("slimtubetests", SLIMTUBETEST_RECORD),
        ("samplesanalysesreport", storage_mock_objects.SAMPLESANALYSESREPORT_RECORD),
        ("capillarypressuretests", SAMPLESANALYSIS_RECORD),
        ("relativepermeabilitytests", SAMPLESANALYSIS_RECORD),
        ("fractionationtests", SAMPLESANALYSIS_RECORD),
        ("extractiontests", SAMPLESANALYSIS_RECORD),
        ("physicalchemistrytests", SAMPLESANALYSIS_RECORD),
        ("electricalproperties", SAMPLESANALYSIS_RECORD),
        ("rockcompressibilities", SAMPLESANALYSIS_RECORD),
        ("watergasrelativepermeabilities", SAMPLESANALYSIS_RECORD),
        ("formationresistivityindexes", SAMPLESANALYSIS_RECORD),
    ],
)
async def test_post_record_auth_errors(
    path, osdu_record,
):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.post(
            f"/api/os-rafs-ddms/{API_VERSION}/{path}",
            headers=TEST_HEADERS_NO_AUTH,
            json=[osdu_record.dict(exclude_none=True)],
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint,record_id", [
        (CORING_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (CORING_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (CORING_ENDPOINT_PATH, TEST_CCE_ID),
        (CORING_ENDPOINT_PATH, TEST_DL_ID),
        (CORING_ENDPOINT_PATH, TEST_TRANSPORT_ID),
        (CORING_ENDPOINT_PATH, TEST_COMPOSITIONALANALYSIS_ID),
        (PVT_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (PVT_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_CORING_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_CCE_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_DL_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_TRANSPORT_ID),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, TEST_CORING_ID),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, TEST_CCE_ID),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, TEST_DL_ID),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, TEST_TRANSPORT_ID),
        (CCE_ENDPOINT_PATH, TEST_CORING_ID),
        (CCE_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (CCE_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (DIF_LIB_ENDPOINT_PATH, TEST_CORING_ID),
        (DIF_LIB_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (DIF_LIB_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (TRANSPORT_ENDPOINT_PATH, TEST_CORING_ID),
        (TRANSPORT_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (TRANSPORT_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (COMPOSITIONALANALYSIS_ENDPOINT_PATH, TEST_CORING_ID),
        (COMPOSITIONALANALYSIS_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (COMPOSITIONALANALYSIS_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (MSS_ENDPOINT_PATH, TEST_CORING_ID),
        (MSS_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (MSS_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (SWELLING_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (WATERANALYSIS_ENDPOINT_PATH, TEST_COMPOSITIONALANALYSIS_ID),
        (STO_ENDPOINT_PATH, TEST_CORING_ID),
        (STO_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (STO_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (INTERFACIAL_TENSION_ENDPOINT_PATH, TEST_CORING_ID),
        (INTERFACIAL_TENSION_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (INTERFACIAL_TENSION_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (VLE_ENDPOINT_PATH, TEST_CORING_ID),
        (VLE_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (VLE_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (MCM_ENDPOINT_PATH, TEST_PVT_ID),
        (SLIMTUBETEST_ENDPOINT_PATH, TEST_CORING_ID),
        (SLIMTUBETEST_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (SLIMTUBETEST_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (storage_mock_objects.SAMPLESANALYSES_ENDPOINT_PATH, TEST_CORING_ID),
        (CAP_PRESSURE_ENDPOINT_PATH, TEST_CORING_ID),
        (CAP_PRESSURE_ENDPOINT_PATH, TEST_ROCKSAMPLE_ID),
        (CAP_PRESSURE_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (RELATIVE_PERMEABILITY_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (FRACTIONATION_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (EXTRACTION_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (PHYS_CHEM_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (ELECTRICAL_PROPERTIES_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (ROCK_COMPRESSIBILITY_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
        (FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH, TEST_ROCKSAMPLEANALYSIS_ID),
    ],
)
async def test_get_record_wrong_kind(endpoint, record_id):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{endpoint}/{record_id}",
                headers=TEST_HEADERS,
            )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint,manifest", [
        (CORING_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (PVT_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (ROCKSAMPLE_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (ROCKSAMPLEANALYSIS_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (DIF_LIB_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (COMPOSITIONALANALYSIS_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (MSS_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (SWELLING_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (CVD_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (WATERANALYSIS_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (STO_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (INTERFACIAL_TENSION_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (VLE_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (MCM_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (SLIMTUBETEST_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (storage_mock_objects.SAMPLESANALYSES_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (CAP_PRESSURE_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (RELATIVE_PERMEABILITY_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (FRACTIONATION_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (EXTRACTION_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (PHYS_CHEM_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (ELECTRICAL_PROPERTIES_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (ROCK_COMPRESSIBILITY_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
        (FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH, OSDU_GENERIC_RECORD.dict()),
    ],
)
async def test_post_record_wrong_kind(endpoint, manifest):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                endpoint,
                headers=TEST_HEADERS,
                json=[manifest],
            )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint,record_id", [
        (CORING_ENDPOINT_PATH, TEST_WRONG_ID),
        (PVT_ENDPOINT_PATH, TEST_WRONG_ID),
        (ROCKSAMPLE_ENDPOINT_PATH, TEST_WRONG_ID),
        (CCE_ENDPOINT_PATH, TEST_WRONG_ID),
        (DIF_LIB_ENDPOINT_PATH, TEST_WRONG_ID),
        (TRANSPORT_ENDPOINT_PATH, TEST_WRONG_ID),
        (COMPOSITIONALANALYSIS_ENDPOINT_PATH, TEST_WRONG_ID),
        (MSS_ENDPOINT_PATH, TEST_WRONG_ID),
        (SWELLING_ENDPOINT_PATH, TEST_WRONG_ID),
        (CVD_ENDPOINT_PATH, TEST_WRONG_ID),
        (WATERANALYSIS_ENDPOINT_PATH, TEST_WRONG_ID),
        (STO_ENDPOINT_PATH, TEST_WRONG_ID),
        (INTERFACIAL_TENSION_ENDPOINT_PATH, TEST_WRONG_ID),
        (VLE_ENDPOINT_PATH, TEST_WRONG_ID),
        (MCM_ENDPOINT_PATH, TEST_WRONG_ID),
        (SLIMTUBETEST_ENDPOINT_PATH, TEST_WRONG_ID),
        (storage_mock_objects.SAMPLESANALYSES_ENDPOINT_PATH, TEST_WRONG_ID),
        (CAP_PRESSURE_ENDPOINT_PATH, TEST_WRONG_ID),
        (RELATIVE_PERMEABILITY_ENDPOINT_PATH, TEST_WRONG_ID),
        (FRACTIONATION_ENDPOINT_PATH, TEST_WRONG_ID),
        (EXTRACTION_ENDPOINT_PATH, TEST_WRONG_ID),
        (PHYS_CHEM_ENDPOINT_PATH, TEST_WRONG_ID),
        (ELECTRICAL_PROPERTIES_ENDPOINT_PATH, TEST_WRONG_ID),
        (ROCK_COMPRESSIBILITY_ENDPOINT_PATH, TEST_WRONG_ID),
        (WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH, TEST_WRONG_ID),
        (FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH, TEST_WRONG_ID),
    ],
)
async def test_delete_record_wrong_kind(endpoint, record_id):
    with storage_override():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.delete(
                f"{endpoint}/{record_id}",
                headers=TEST_HEADERS,
            )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
