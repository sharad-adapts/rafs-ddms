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

import json
from contextlib import contextmanager
from unittest.mock import create_autospec, patch

import pandas as pd
import pyarrow as pa
import pytest
from httpx import AsyncClient
from pyarrow import parquet as pq
from starlette import status

from app.api.dependencies.services import (
    get_async_dataset_service,
    get_async_storage_service,
)
from app.api.routes.utils.query import find_osdu_ids_from_string
from app.main import app
from app.services import dataset, storage
from tests.test_api.test_routes import dependencies
from tests.test_api.test_routes.api_v2.cappressure import (
    cappressure_mock_objects,
)
from tests.test_api.test_routes.api_v2.electricalproperties import (
    electricalproperties_mock_objects as electricalproperties_mock_objects_api_v2,
)
from tests.test_api.test_routes.bulk_pyrolysis import (
    bulk_pyrolysis_mock_objects,
)
from tests.test_api.test_routes.cec_content import cec_content_mock_objects
from tests.test_api.test_routes.core_gamma import core_gamma_mock_objects
from tests.test_api.test_routes.data import data_mock_objects
from tests.test_api.test_routes.data.data_mock_objects import (
    INVALID_DATA_WITH_NAN,
    ORIENT_SPLIT_400_PAYLOADS,
    TEST_HEADERS_IMPROPER_SCHEMA_VERSION,
    TEST_HEADERS_JSON,
    TEST_HEADERS_NO_AUTH,
    TEST_HEADERS_PARQUET,
    TEST_HEADERS_WITHOUT_SCHEMA_VERSION,
    TEST_SERVER,
    build_get_test_data,
    build_mock_get_dataset_service,
    build_mock_get_storage_service,
)
from tests.test_api.test_routes.eds_mapping_data import (
    eds_mapping_data_mock_objects,
)
from tests.test_api.test_routes.gas_chromatography import (
    gas_chromatography_mock_objects,
)
from tests.test_api.test_routes.gas_composition import (
    gas_composition_mock_objects,
)
from tests.test_api.test_routes.gcms_alkanes import gcms_alkanes_mock_objects
from tests.test_api.test_routes.gcms_aromatics import (
    gcms_aromatics_mock_objects,
)
from tests.test_api.test_routes.gcms_ratios import gcms_ratios_mock_objects
from tests.test_api.test_routes.gcmsms_analysis import (
    gcmsms_analysis_mock_objects,
)
from tests.test_api.test_routes.isotope_analysis import (
    isotope_analysis_mock_objects,
)
from tests.test_api.test_routes.mercuryinjection import (
    mercuryinjection_mock_objects,
)
from tests.test_api.test_routes.multiple_salinity import (
    multiple_salinity_mock_objects,
)
from tests.test_api.test_routes.nmr import nmr_mock_objects
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
    CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
    CEC_CONTENT_ENDPOINT_PATH_API_V2,
    CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
    EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
    ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
    GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
    GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
    GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
    GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
    GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
    GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
    ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
    MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
    MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
    NMR_DATA_ENDPOINT_PATH_API_V2,
    RCA_DATA_ENDPOINT_PATH_API_V2,
    TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
    UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
    WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
    BulkDatasetIdV2,
)
from tests.test_api.test_routes.routine_core_analysis import rca_mock_objects
from tests.test_api.test_routes.triaxial_test import triaxial_test_mock_objects
from tests.test_api.test_routes.uniaxial_test import uniaxial_test_mock_objects
from tests.test_api.test_routes.wettability_index import (
    wettability_index_mock_objects,
)

async_storage_record_service_mock = create_autospec(storage.StorageService, spec_set=True, instance=True)
async_dataset_service_mock = create_autospec(dataset.DatasetService, spec_set=True, instance=True)


async def mock_get_async_dataset_service():
    yield async_dataset_service_mock


async def mock_get_storage_service():
    yield async_storage_record_service_mock


async def mock_get_async_storage_service():
    yield async_storage_record_service_mock


@contextmanager
def services_overrides():
    overrides = {
        get_async_storage_service: mock_get_async_storage_service,
        get_async_dataset_service: mock_get_async_dataset_service,
    }
    with dependencies.DependencyOverrider(app, overrides) as mock_dependencies:
        yield mock_dependencies


@pytest.fixture
def with_patched_storage_failed_integrity_validation(missed_records):
    """Patch storage query_records failure."""
    query_response = {
        "invalidRecords": missed_records,
    }
    with patch.object(async_storage_record_service_mock, "query_records", return_value=query_response):
        yield


@pytest.fixture
def with_patched_services_success(storage_method, osdu_records, dataset_method, blobs):
    """Patch storage and datasets to 200 success."""
    with patch.object(async_storage_record_service_mock, storage_method, side_effect=osdu_records):
        with patch.object(async_dataset_service_mock, dataset_method, side_effect=blobs):
            yield


@contextmanager
def post_overrides(record_data=None, test_dataset_record_id=data_mock_objects.TEST_DATASET_RECORD_ID, data_payload=None):
    mock_get_storage_service = build_mock_get_storage_service(record_data, data_payload)
    mock_get_dataset_service = build_mock_get_dataset_service(test_dataset_record_id=test_dataset_record_id)
    overrides = {
        get_async_storage_service: mock_get_storage_service,
        get_async_dataset_service: mock_get_dataset_service,
    }
    with dependencies.DependencyOverrider(app, overrides) as mock_dependencies:
        yield mock_dependencies


@pytest.mark.parametrize(
    "data_endpoint_path,dataset_id", [
        (RCA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.RCA),
        (NMR_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_RATIOS),
        (GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_CHROMATOGRAPHY),
        (GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_COMPOSITION),
        (ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ISOTOPE_ANALYSIS),
        (BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.BULK_PYROLYSIS),
        (CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CORE_GAMMA),
        (UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.UNIAXIAL_TEST),
        (WETTABILITY_INDEX_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.WETTABILITY_INDEX),
        (GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMSMS_ANALYSIS),
        (CEC_CONTENT_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CEC_CONTENT),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ELECTRICAL_PROPERTIES),
        (TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.TRIAXIAL_TEST),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CAP_PRESSURE),
        (EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.EDS_MAPPING),

    ],
)
@pytest.mark.asyncio
async def test_get_content_data_no_data(data_endpoint_path, dataset_id):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{data_endpoint_path}/{dataset_id}",
                headers=TEST_HEADERS_PARQUET,
            )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    expected = {"message": f"{dataset_id} does not exist in current record.", "reason": "Not found."}
    assert response.json() == expected


@pytest.mark.parametrize(
    "data_endpoint_path,dataset_id", [
        (RCA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.RCA),
        (NMR_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_RATIOS),
        (GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_CHROMATOGRAPHY),
        (GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_COMPOSITION),
        (ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ISOTOPE_ANALYSIS),
        (BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.BULK_PYROLYSIS),
        (CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CORE_GAMMA),
        (UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.UNIAXIAL_TEST),
        (WETTABILITY_INDEX_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.WETTABILITY_INDEX),
        (GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMSMS_ANALYSIS),
        (CEC_CONTENT_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CEC_CONTENT),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ELECTRICAL_PROPERTIES),
        (TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.TRIAXIAL_TEST),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CAP_PRESSURE),
        (EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.EDS_MAPPING),
    ],
)
@pytest.mark.asyncio
async def test_get_rca_data_no_content_header(data_endpoint_path, dataset_id):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{data_endpoint_path}/{dataset_id}",
                headers=None,
            )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected = {"code": status.HTTP_400_BAD_REQUEST, "reason": "Content-Type header is required, but was not provided"}
    assert response.json() == expected


@pytest.mark.parametrize(
    "data_endpoint_path,dataset_id", [
        (RCA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.RCA),
        (NMR_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMS_RATIOS),
        (GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_CHROMATOGRAPHY),
        (GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GAS_COMPOSITION),
        (ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ISOTOPE_ANALYSIS),
        (BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.BULK_PYROLYSIS),
        (CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CORE_GAMMA),
        (UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.UNIAXIAL_TEST),
        (WETTABILITY_INDEX_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.WETTABILITY_INDEX),
        (GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.GCMSMS_ANALYSIS),
        (CEC_CONTENT_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CEC_CONTENT),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.ELECTRICAL_PROPERTIES),
        (TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.TRIAXIAL_TEST),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.CAP_PRESSURE),
        (EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2, BulkDatasetIdV2.EDS_MAPPING),
    ],
)
@pytest.mark.asyncio
async def test_get_rca_data_wrong_content_header(data_endpoint_path, dataset_id):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{data_endpoint_path}/{dataset_id}",
                headers={"Content-Type": "wrong-type"},
            )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected = {
        "code": status.HTTP_400_BAD_REQUEST,
        "reason": "The provided content-type is not supported. Please provide one of the next supported content types: ['application/json', 'application/x-parquet']",
    }
    assert response.json() == expected


@pytest.mark.parametrize(
    "data_endpoint_path,dataset_id,storage_method,osdu_records,dataset_method,blobs",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_content_parquet_data(
    data_endpoint_path,
    dataset_id,
    storage_method,
    osdu_records,
    dataset_method,
    blobs,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{data_endpoint_path}/{dataset_id}",
                headers=TEST_HEADERS_PARQUET,
            )
    arrow_table = pq.read_table(pa.BufferReader(blobs[0]))
    assert response.status_code == status.HTTP_200_OK
    assert pq.read_table(pa.BufferReader(response.content)).equals(arrow_table)


@pytest.mark.parametrize(
    "data_endpoint_path,params,storage_method,osdu_records,dataset_method,blobs,returned_data", [
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_DATA,
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            rca_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            nmr_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            multiple_salinity_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_alkanes_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            mercuryinjection_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_aromatics_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_ratios_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            gas_chromatography_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            gas_composition_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            isotope_analysis_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            bulk_pyrolysis_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            core_gamma_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            uniaxial_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            wettability_index_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            gcmsms_analysis_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects_api_v2.TEST_PARAMS_AGGREGATION,
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_AGGREGATED_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            cec_content_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            triaxial_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            eds_mapping_data_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            rca_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            nmr_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            multiple_salinity_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_alkanes_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            mercuryinjection_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_aromatics_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_ratios_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            gas_chromatography_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            gas_composition_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            isotope_analysis_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            bulk_pyrolysis_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            core_gamma_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            uniaxial_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            wettability_index_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            gcmsms_analysis_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            cec_content_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects_api_v2.TEST_PARAMS_FILTERS,
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_FILTERED_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            triaxial_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            eds_mapping_data_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_FILTERED_DATA,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_data_json_data(
    data_endpoint_path,
    params,
    storage_method,
    osdu_records,
    dataset_method,
    blobs,
    returned_data,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                params=params,
            )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["index"] == returned_data["index"]
    assert set(response.json()["columns"]) == set(returned_data["columns"])
    assert all(i in response.json()["data"][0] for i in returned_data["data"][0])


@pytest.mark.parametrize(
    "data_endpoint_path,storage_method,osdu_records,dataset_method,blobs,returned_data", [
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_DATA,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_data_json_data_no_content_schema_version(
    data_endpoint_path,
    storage_method,
    osdu_records,
    dataset_method,
    blobs,
    returned_data,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                data_endpoint_path,
                headers=TEST_HEADERS_WITHOUT_SCHEMA_VERSION,
            )
    expected_error = {
        "code": status.HTTP_400_BAD_REQUEST,
        "reason": "No schema version specified or invalid schema format. Check if the schema version is specified in the 'Accept' header. Example: --header 'Accept: */*;version=1.0.0'",
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_error


@pytest.mark.parametrize(
    "data_endpoint_path,storage_method,osdu_records,dataset_method,blobs,returned_data", [
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_DATA,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_data_json_data_improper_schema_version(
    data_endpoint_path,
    storage_method,
    osdu_records,
    dataset_method,
    blobs,
    returned_data,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                data_endpoint_path,
                headers=TEST_HEADERS_IMPROPER_SCHEMA_VERSION,
            )
    expected_error = {
        "code": status.HTTP_400_BAD_REQUEST,
        "reason": "No schema version specified or invalid schema format. Check if the schema version is specified in the 'Accept' header. Example: --header 'Accept: */*;version=1.0.0'",
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_error


@pytest.mark.parametrize(
    "data_endpoint_path,storage_method,osdu_records,dataset_method,blobs,returned_data", [
        (
            f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rca_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rca_mock_objects.TEST_DATA)],
            rca_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_chromatography_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_chromatography_mock_objects.TEST_DATA)],
            gas_chromatography_mock_objects.TEST_DATA,
        ),
        (
            f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gas_composition_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gas_composition_mock_objects.TEST_DATA)],
            gas_composition_mock_objects.TEST_DATA,
        ),
        (
            f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [isotope_analysis_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", isotope_analysis_mock_objects.TEST_DATA)],
            isotope_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", bulk_pyrolysis_mock_objects.TEST_DATA)],
            bulk_pyrolysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [core_gamma_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", core_gamma_mock_objects.TEST_DATA)],
            core_gamma_mock_objects.TEST_DATA,
        ),
        (
            f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [uniaxial_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", uniaxial_test_mock_objects.TEST_DATA)],
            uniaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [wettability_index_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", wettability_index_mock_objects.TEST_DATA)],
            wettability_index_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcmsms_analysis_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcmsms_analysis_mock_objects.TEST_DATA)],
            gcmsms_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cec_content_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cec_content_mock_objects.TEST_DATA)],
            cec_content_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects_api_v2.TEST_DATA)],
            electricalproperties_mock_objects_api_v2.TEST_DATA,
        ),
        (
            f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [triaxial_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", triaxial_test_mock_objects.TEST_DATA)],
            triaxial_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [eds_mapping_data_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", eds_mapping_data_mock_objects.TEST_DATA)],
            eds_mapping_data_mock_objects.TEST_DATA,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_data_json_data_no_schema_version_for_dataset(
    data_endpoint_path,
    storage_method,
    osdu_records,
    dataset_method,
    blobs,
    returned_data,
    with_patched_services_success,
):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
            )
    expected_error = {
        "code": status.HTTP_400_BAD_REQUEST,
        "reason": "Invalid schema version has been provided. Schema version 1.0.0 is not one of proper versions: {'2.0.0'}",
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_error


@pytest.mark.parametrize(
    "data_endpoint_path,record_data,test_data,test_dataset_record_id,test_ddms_urn",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rca_mock_objects.TEST_DATA,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
            rca_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_chromatography_mock_objects.TEST_DATA,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
            gas_chromatography_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_composition_mock_objects.TEST_DATA,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
            gas_composition_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            isotope_analysis_mock_objects.TEST_DATA,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            isotope_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            bulk_pyrolysis_mock_objects.TEST_DATA,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
            bulk_pyrolysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            core_gamma_mock_objects.TEST_DATA,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
            core_gamma_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            uniaxial_test_mock_objects.TEST_DATA,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            uniaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            wettability_index_mock_objects.TEST_DATA,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
            wettability_index_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcmsms_analysis_mock_objects.TEST_DATA,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            gcmsms_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cec_content_mock_objects.TEST_DATA,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
            cec_content_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects_api_v2.TEST_DATA,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects_api_v2.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            triaxial_test_mock_objects.TEST_DATA,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            triaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            eds_mapping_data_mock_objects.TEST_DATA,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
            eds_mapping_data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_data_json(data_endpoint_path, record_data, test_data, test_dataset_record_id, test_ddms_urn):
    with post_overrides(record_data, test_dataset_record_id, test_data):
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(test_data),
            )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["ddms_urn"] == test_ddms_urn
    assert test_ddms_urn in record_data["data"]["DDMSDatasets"]


@pytest.mark.parametrize(
    "data_endpoint_path,record_data,test_data,test_dataset_record_id,test_ddms_urn",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rca_mock_objects.TEST_DATA,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
            rca_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_chromatography_mock_objects.TEST_DATA,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
            gas_chromatography_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_composition_mock_objects.TEST_DATA,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
            gas_composition_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            isotope_analysis_mock_objects.TEST_DATA,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            isotope_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            bulk_pyrolysis_mock_objects.TEST_DATA,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
            bulk_pyrolysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            core_gamma_mock_objects.TEST_DATA,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
            core_gamma_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            uniaxial_test_mock_objects.TEST_DATA,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            uniaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            wettability_index_mock_objects.TEST_DATA,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
            wettability_index_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcmsms_analysis_mock_objects.TEST_DATA,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            gcmsms_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cec_content_mock_objects.TEST_DATA,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
            cec_content_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects_api_v2.TEST_DATA,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects_api_v2.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            triaxial_test_mock_objects.TEST_DATA,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            triaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            eds_mapping_data_mock_objects.TEST_DATA,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
            eds_mapping_data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_data_json_no_ddmsdatasets_field(
        data_endpoint_path, record_data, test_data, test_dataset_record_id, test_ddms_urn,
):
    del record_data["data"]["DDMSDatasets"]
    with post_overrides(record_data, test_dataset_record_id, test_data):
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(test_data),
            )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["ddms_urn"] == test_ddms_urn
    assert test_ddms_urn in record_data["data"]["DDMSDatasets"]


@pytest.mark.parametrize(
    "data_endpoint_path,record_data,test_dataset_record_id",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_data_parquet_empty(data_endpoint_path, record_data, test_dataset_record_id):
    with post_overrides(record_data, test_dataset_record_id):
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_PARQUET,
                content=b"",
            )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "data_endpoint_path,record_data,test_data,test_dataset_record_id,test_ddms_urn",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rca_mock_objects.TEST_DATA,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
            rca_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_chromatography_mock_objects.TEST_DATA,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
            gas_chromatography_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_composition_mock_objects.TEST_DATA,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
            gas_composition_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            isotope_analysis_mock_objects.TEST_DATA,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            isotope_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            bulk_pyrolysis_mock_objects.TEST_DATA,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
            bulk_pyrolysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            core_gamma_mock_objects.TEST_DATA,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
            core_gamma_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            uniaxial_test_mock_objects.TEST_DATA,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            uniaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            wettability_index_mock_objects.TEST_DATA,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
            wettability_index_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcmsms_analysis_mock_objects.TEST_DATA,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            gcmsms_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cec_content_mock_objects.TEST_DATA,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
            cec_content_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects_api_v2.TEST_DATA,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects_api_v2.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            triaxial_test_mock_objects.TEST_DATA,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            triaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            eds_mapping_data_mock_objects.TEST_DATA,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
            eds_mapping_data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_data_parquet(data_endpoint_path, record_data, test_data, test_dataset_record_id, test_ddms_urn):
    dataframe = pd.DataFrame(test_data["data"], columns=test_data["columns"])

    with post_overrides(record_data, test_dataset_record_id, dataframe):
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_PARQUET,
                content=dataframe.to_parquet(),
            )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["ddms_urn"] == test_ddms_urn
    assert test_ddms_urn in record_data["data"]["DDMSDatasets"]


@pytest.mark.parametrize(
    "data_endpoint_path,record_data,test_data,test_dataset_record_id,test_ddms_urn",
    [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rca_mock_objects.TEST_DATA,
            rca_mock_objects.TEST_DATASET_RECORD_ID,
            rca_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_chromatography_mock_objects.TEST_DATA,
            gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID,
            gas_chromatography_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gas_composition_mock_objects.TEST_DATA,
            gas_composition_mock_objects.TEST_DATASET_RECORD_ID,
            gas_composition_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            isotope_analysis_mock_objects.TEST_DATA,
            isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            isotope_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            bulk_pyrolysis_mock_objects.TEST_DATA,
            bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID,
            bulk_pyrolysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            core_gamma_mock_objects.TEST_DATA,
            core_gamma_mock_objects.TEST_DATASET_RECORD_ID,
            core_gamma_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            uniaxial_test_mock_objects.TEST_DATA,
            uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            uniaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            wettability_index_mock_objects.TEST_DATA,
            wettability_index_mock_objects.TEST_DATASET_RECORD_ID,
            wettability_index_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcmsms_analysis_mock_objects.TEST_DATA,
            gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            gcmsms_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cec_content_mock_objects.TEST_DATA,
            cec_content_mock_objects.TEST_DATASET_RECORD_ID,
            cec_content_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects_api_v2.TEST_DATA,
            electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects_api_v2.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            triaxial_test_mock_objects.TEST_DATA,
            triaxial_test_mock_objects.TEST_DATASET_RECORD_ID,
            triaxial_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            eds_mapping_data_mock_objects.TEST_DATA,
            eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID,
            eds_mapping_data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_data_new_dataset(data_endpoint_path, record_data, test_data, test_dataset_record_id, test_ddms_urn):
    with post_overrides(record_data, test_dataset_record_id, test_data):
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(test_data),
            )
            body = response.json()

    assert body["ddms_urn"] == test_ddms_urn


@pytest.mark.parametrize(
    "data_endpoint_path, incorrect_schema_test_data", [
        (RCA_DATA_ENDPOINT_PATH_API_V2, rca_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (NMR_DATA_ENDPOINT_PATH_API_V2, nmr_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2, multiple_salinity_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2, gcms_alkanes_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2, mercuryinjection_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2, gcms_aromatics_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2, gcms_ratios_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2, gas_chromatography_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2, gas_composition_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, isotope_analysis_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2, bulk_pyrolysis_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2, core_gamma_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, uniaxial_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (WETTABILITY_INDEX_ENDPOINT_PATH_API_V2, wettability_index_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, gcmsms_analysis_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CEC_CONTENT_ENDPOINT_PATH_API_V2, cec_content_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2, electricalproperties_mock_objects_api_v2.INCORRECT_SCHEMA_TEST_DATA),
        (TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, triaxial_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2, cappressure_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2, eds_mapping_data_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
    ],
)
@pytest.mark.asyncio
async def test_post_rca_data_validation_error(data_endpoint_path, incorrect_schema_test_data):
    with post_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(incorrect_schema_test_data),
            )

    body = response.json()
    assert ["code", "reason", "errors"] == list(body.keys())
    assert body["reason"] == "Data validation failed."
    reason = body["errors"]
    assert isinstance(reason, dict)
    assert len(reason) == 1
    assert set(reason.keys()) == {"Invalid type"}


@pytest.mark.parametrize(
    "data_endpoint_path,incorrect_dataframe_data,error_reason", [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2,
            rca_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            rca_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            NMR_DATA_ENDPOINT_PATH_API_V2,
            nmr_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            nmr_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
            multiple_salinity_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            multiple_salinity_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
            gcms_alkanes_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_alkanes_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
            mercuryinjection_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            mercuryinjection_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
            gcms_aromatics_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_aromatics_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
            gcms_ratios_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_ratios_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
            gas_chromatography_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gas_chromatography_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
            gas_composition_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gas_composition_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            isotope_analysis_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            isotope_analysis_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
            bulk_pyrolysis_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            bulk_pyrolysis_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
            core_gamma_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            core_gamma_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            uniaxial_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            uniaxial_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
            wettability_index_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            wettability_index_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
            gcmsms_analysis_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcmsms_analysis_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            CEC_CONTENT_ENDPOINT_PATH_API_V2,
            cec_content_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            cec_content_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
            electricalproperties_mock_objects_api_v2.INCORRECT_DATAFRAME_TEST_DATA,
            electricalproperties_mock_objects_api_v2.EXPECTED_ERROR_REASON,
        ),
        (
            TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
            triaxial_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            triaxial_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
            cappressure_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            cappressure_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
            eds_mapping_data_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            eds_mapping_data_mock_objects.EXPECTED_ERROR_REASON,
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_rca_invalid_df_error(data_endpoint_path, incorrect_dataframe_data, error_reason):
    with post_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(incorrect_dataframe_data),
            )

    body = response.json()
    assert ["code", "reason"] == list(body.keys())
    assert body["reason"] == error_reason


@pytest.mark.parametrize(
    "data_endpoint_path", [
        f"{RCA_DATA_ENDPOINT_PATH_API_V2}/{rca_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{NMR_DATA_ENDPOINT_PATH_API_V2}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2}/{gas_chromatography_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2}/{gas_composition_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{isotope_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2}/{bulk_pyrolysis_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2}/{core_gamma_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{uniaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{WETTABILITY_INDEX_ENDPOINT_PATH_API_V2}/{wettability_index_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2}/{gcmsms_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CEC_CONTENT_ENDPOINT_PATH_API_V2}/{cec_content_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2}/{electricalproperties_mock_objects_api_v2.TEST_DATASET_RECORD_ID}",
        f"{TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2}/{triaxial_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2}/{eds_mapping_data_mock_objects.TEST_DATASET_RECORD_ID}",
    ],
)
@pytest.mark.asyncio
async def test_rca_get_403(data_endpoint_path):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.get(
            data_endpoint_path,
            headers=TEST_HEADERS_NO_AUTH,
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "data_endpoint_path", [
        RCA_DATA_ENDPOINT_PATH_API_V2,
        NMR_DATA_ENDPOINT_PATH_API_V2,
        MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
        GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
        MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
        GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
        GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
        GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
        GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
        ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
        BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
        CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
        UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
        WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
        GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
        CEC_CONTENT_ENDPOINT_PATH_API_V2,
        ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
        TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
        CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
        EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
    ],
)
@pytest.mark.asyncio
async def test_rca_post_403(data_endpoint_path):
    async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
        response = await client.post(
            data_endpoint_path,
            headers=TEST_HEADERS_NO_AUTH,
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "data_endpoint_path,integrity_error_dataframe_data,missed_records", [
        (
            RCA_DATA_ENDPOINT_PATH_API_V2, rca_mock_objects.TEST_DATA, list(
                find_osdu_ids_from_string(json.dumps(rca_mock_objects.TEST_DATA)),
            ),
        ),
    ],
)
@pytest.mark.asyncio
async def test_post_rca_integrity_error(data_endpoint_path, integrity_error_dataframe_data, missed_records, with_patched_storage_failed_integrity_validation):
    with services_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(integrity_error_dataframe_data),
            )

    body = response.json()
    assert ["code", "reason", "errors"] == list(body.keys())
    assert body["reason"] == "Data validation failed."
    errors = body["errors"]
    assert errors.get("Missing records in storage", []).sort() == missed_records.sort()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        RCA_DATA_ENDPOINT_PATH_API_V2,
        NMR_DATA_ENDPOINT_PATH_API_V2,
        MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2,
        GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2,
        MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2,
        GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2,
        GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2,
        GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2,
        GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2,
        ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
        BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2,
        CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2,
        UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
        WETTABILITY_INDEX_ENDPOINT_PATH_API_V2,
        GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2,
        CEC_CONTENT_ENDPOINT_PATH_API_V2,
        ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2,
        TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2,
        CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2,
        EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2,
    ],
)
async def test_invalid_data_with_nan(path):
    with post_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.post(
                path,
                headers=TEST_HEADERS_JSON,
                content=json.dumps(INVALID_DATA_WITH_NAN),
            )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = response.json()
    assert ["code", "reason", "errors"] == list(body.keys())
    assert body["reason"] == "Data validation failed."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,payloads",
    [
        (RCA_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (NMR_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GAS_CHROMATOGRAPHY_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GAS_COMPOSITION_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (ISOTOPE_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (BULK_PYROLYSIS_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (CORE_GAMMA_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (UNIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (WETTABILITY_INDEX_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (GCMSMS_ANALYSIS_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (CEC_CONTENT_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (TRIAXIAL_TEST_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
        (EDS_MAPPING_DATA_ENDPOINT_PATH_API_V2, ORIENT_SPLIT_400_PAYLOADS),
    ],
)
async def test_invalid_data_json_payload(path, payloads):
    for payload in payloads:
        with post_overrides():
            async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
                response = await client.post(
                    path,
                    headers=TEST_HEADERS_JSON,
                    content=json.dumps(payload),
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        body = response.json()

        assert ["code", "reason"] == list(body.keys())
        assert body["reason"].startswith("Data error:")
