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
import re
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
from app.main import app
from app.resources.common_headers import CONTENT_TYPE
from app.resources.mime_types import SupportedMimeTypes
from app.services import dataset, storage
from tests.test_api.test_routes import dependencies
from tests.test_api.test_routes.cappressure import cappressure_mock_objects
from tests.test_api.test_routes.cce import cce_mock_objects
from tests.test_api.test_routes.compositionalanalysis import (
    compositionalanalysis_mock_objects,
)
from tests.test_api.test_routes.cvd import cvd_mock_objects
from tests.test_api.test_routes.data import data_mock_objects
from tests.test_api.test_routes.data.data_mock_objects import (
    INVALID_DATA_WITH_NAN,
    MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
    MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
    NO_DATASETS_DATASET_SIDE_EFFECT,
    NO_DATASETS_STORAGE_SIDE_EFFECT,
    ORIENT_SPLIT_400_PAYLOADS,
    SINGLE_DATASET_DATASET_SIDE_EFFECT,
    SINGLE_DATASET_STORAGE_SIDE_EFFECT,
    TEST_DATA,
    TEST_HEADERS_IMPROPER_SCHEMA_VERSION,
    TEST_HEADERS_JSON,
    TEST_HEADERS_NO_AUTH,
    TEST_HEADERS_PARQUET,
    TEST_HEADERS_WITHOUT_SCHEMA_VERSION,
    TEST_SERVER,
    TEST_WRONG_AGGREGATION_REASONS,
    TEST_WRONG_COLUMNS_FILTERS_REASONS,
    TEST_WRONG_ROWS_FILTERS_REASONS,
    build_get_test_data,
    build_mock_get_dataset_service,
    build_mock_get_storage_service,
)
from tests.test_api.test_routes.dif_lib import dif_lib_mock_objects
from tests.test_api.test_routes.electricalproperties import (
    electricalproperties_mock_objects,
)
from tests.test_api.test_routes.extraction import extraction_mock_objects
from tests.test_api.test_routes.formationresistivityindex import (
    formationresistivityindex_mock_objects,
)
from tests.test_api.test_routes.fractionation import fractionation_mock_objects
from tests.test_api.test_routes.gcms_alkanes import gcms_alkanes_mock_objects
from tests.test_api.test_routes.gcms_aromatics import (
    gcms_aromatics_mock_objects,
)
from tests.test_api.test_routes.gcms_ratios import gcms_ratios_mock_objects
from tests.test_api.test_routes.interfacialtension import (
    interfacialtension_test_mock_objects,
)
from tests.test_api.test_routes.mcm import mcm_mock_objects
from tests.test_api.test_routes.mercuryinjection import (
    mercuryinjection_mock_objects,
)
from tests.test_api.test_routes.multiple_salinity import (
    multiple_salinity_mock_objects,
)
from tests.test_api.test_routes.multistageseparator import mss_test_mock_objects
from tests.test_api.test_routes.nmr import nmr_mock_objects
from tests.test_api.test_routes.osdu.storage_mock_objects import (
    CAP_PRESSURE_DATA_ENDPOINT_PATH,
    CCE_DATA_ENDPOINT_PATH,
    CCE_SOURCE_ENDPOINT_PATH,
    COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
    COMPOSITIONALANALYSIS_SOURCE_ENDPOINT_PATH,
    CVD_DATA_ENDPOINT_PATH,
    CVD_SOURCE_ENDPOINT_PATH,
    DIF_LIB_DATA_ENDPOINT_PATH,
    DIF_LIB_SOURCE_ENDPOINT_PATH,
    ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
    ELECTRICAL_PROPERTIES_SOURCE_ENDPOINT_PATH,
    EXTRACTION_DATA_ENDPOINT_PATH,
    EXTRACTION_SOURCE_ENDPOINT_PATH,
    FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
    FORMATION_RESISTIVITY_INDEX_SOURCE_ENDPOINT_PATH,
    FRACTIONATION_DATA_ENDPOINT_PATH,
    FRACTIONATION_SOURCE_ENDPOINT_PATH,
    GCMS_ALKANES_DATA_ENDPOINT_PATH,
    GCMS_AROMATICS_DATA_ENDPOINT_PATH,
    GCMS_RATIOS_DATA_ENDPOINT_PATH,
    INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
    INTERFACIAL_TENSION_SOURCE_ENDPOINT_PATH,
    MCM_DATA_ENDPOINT_PATH,
    MCM_SOURCE_ENDPOINT_PATH,
    MERCURY_INJECTION_DATA_ENDPOINT_PATH,
    MSS_DATA_ENDPOINT_PATH,
    MSS_SOURCE_ENDPOINT_PATH,
    MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
    NMR_DATA_ENDPOINT_PATH,
    OSDU_GENERIC_RECORD,
    PHYS_CHEM_DATA_ENDPOINT_PATH,
    PHYS_CHEM_SOURCE_ENDPOINT_PATH,
    PVT_SOURCE_ENDPOINT_PATH,
    RCA_DATA_ENDPOINT_PATH,
    RCA_SOURCE_ENDPOINT_PATH,
    RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
    RELATIVE_PERMEABILITY_SOURCE_ENDPOINT_PATH,
    ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
    SLIMTUBE_DATA_ENDPOINT_PATH,
    SLIMTUBE_SOURCE_ENDPOINT_PATH,
    STO_DATA_ENDPOINT_PATH,
    STO_SOURCE_ENDPOINT_PATH,
    SWELLING_DATA_ENDPOINT_PATH,
    SWELLING_SOURCE_ENDPOINT_PATH,
    TRANSPORT_DATA_ENDPOINT_PATH,
    TRANSPORT_SOURCE_ENDPOINT_PATH,
    VLE_DATA_ENDPOINT_PATH,
    VLE_SOURCE_ENDPOINT_PATH,
    WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
    WATER_GAS_REL_PERM_SOURCE_ENDPOINT_PATH,
    WATERANALYSIS_DATA_ENDPOINT_PATH,
    WATERANALYSIS_SOURCE_ENDPOINT_PATH,
    WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
    BulkDatasetId,
)
from tests.test_api.test_routes.physchem import physchem_mock_objects
from tests.test_api.test_routes.relative_permeability import (
    relative_permeability_mock_objects,
)
from tests.test_api.test_routes.rock_compressibility import (
    rock_compressibility_mock_objects,
)
from tests.test_api.test_routes.slimtubetest import slimtubetest_mock_objects
from tests.test_api.test_routes.sto_test import sto_mock_objects
from tests.test_api.test_routes.swelling_test import swelling_test_mock_objects
from tests.test_api.test_routes.transport_test import (
    transport_test_mock_objects,
)
from tests.test_api.test_routes.vle import vle_mock_objects
from tests.test_api.test_routes.water_analysis import (
    water_analysis_mock_objects,
)
from tests.test_api.test_routes.water_gas_rel_perm import (
    water_gas_rel_perm_mock_objects,
)
from tests.test_api.test_routes.whole_oil_gc import whole_oil_gc_mock_objects

async_storage_record_service_mock = create_autospec(storage.StorageService, spec_set=True, instance=True)
async_dataset_service_mock = create_autospec(dataset.DatasetService, spec_set=True, instance=True)


async def mock_get_async_dataset_service():
    yield async_dataset_service_mock


async def mock_get_storage_service():
    yield async_storage_record_service_mock


async def mock_get_async_storage_service():
    yield async_storage_record_service_mock


@contextmanager
def get_overrides():
    overrides = {
        get_async_storage_service: mock_get_async_storage_service,
        get_async_dataset_service: mock_get_async_dataset_service,
    }
    with dependencies.DependencyOverrider(app, overrides) as mock_dependencies:
        yield mock_dependencies


@pytest.fixture
def with_patched_storage_get_success_200():
    """Patch storage to 200 success."""
    osdu_record = OSDU_GENERIC_RECORD.dict(exclude_none=True)
    with patch.object(async_storage_record_service_mock, "get_record", return_value=osdu_record):
        yield


@pytest.fixture
def with_patched_dataset_post_success_200(test_dataset_record_id=None):
    """Patch dataset to 200 success."""
    with patch.object(async_dataset_service_mock, "upload_file", return_value=test_dataset_record_id):
        yield


@pytest.fixture
def with_patched_services_success(storage_method, osdu_records, dataset_method, blobs):
    """Patch storage and datasets  to 200 success."""
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
        (RCA_DATA_ENDPOINT_PATH, BulkDatasetId.RCA),
        (CCE_DATA_ENDPOINT_PATH, BulkDatasetId.CCE),
        (DIF_LIB_DATA_ENDPOINT_PATH, BulkDatasetId.DIF_LIB),
        (TRANSPORT_DATA_ENDPOINT_PATH, BulkDatasetId.TRANSPORT),
        (MSS_DATA_ENDPOINT_PATH, BulkDatasetId.MSS),
        (COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.CA),
        (SWELLING_DATA_ENDPOINT_PATH, BulkDatasetId.SWELLING),
        (CVD_DATA_ENDPOINT_PATH, BulkDatasetId.CVD),
        (STO_DATA_ENDPOINT_PATH, BulkDatasetId.STO),
        (WATERANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.WA),
        (INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, BulkDatasetId.IT),
        (VLE_DATA_ENDPOINT_PATH, BulkDatasetId.VLE),
        (MCM_DATA_ENDPOINT_PATH, BulkDatasetId.MCM),
        (SLIMTUBE_DATA_ENDPOINT_PATH, BulkDatasetId.SLIMTUBE),
        (RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, BulkDatasetId.RELATIVE_PERMEABILITY),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH, BulkDatasetId.CAP_PRESSURE),
        (FRACTIONATION_DATA_ENDPOINT_PATH, BulkDatasetId.FRACTIONATION),
        (EXTRACTION_DATA_ENDPOINT_PATH, BulkDatasetId.EXTRACTION),
        (PHYS_CHEM_DATA_ENDPOINT_PATH, BulkDatasetId.PHYS_CHEM),
        (WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH, BulkDatasetId.WATER_GAS_RELATIVE_PERMEABILITY),
        (ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, BulkDatasetId.ROCK_COMPRESSIBILITY),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH, BulkDatasetId.ELECTRICAL_PROPERTIES),
        (FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH, BulkDatasetId.FORMATION_RESISTIVITY_INDEX),
        (NMR_DATA_ENDPOINT_PATH, BulkDatasetId.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH, BulkDatasetId.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH, BulkDatasetId.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_RATIOS),
        (WHOLE_OIL_GC_DATA_ENDPOINT_PATH, BulkDatasetId.WHOLE_OIL_GC),
    ],
)
@pytest.mark.asyncio
async def test_get_content_data_no_data(data_endpoint_path, dataset_id, with_patched_storage_get_success_200):
    with get_overrides():
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
        (RCA_DATA_ENDPOINT_PATH, BulkDatasetId.RCA),
        (CCE_DATA_ENDPOINT_PATH, BulkDatasetId.CCE),
        (DIF_LIB_DATA_ENDPOINT_PATH, BulkDatasetId.DIF_LIB),
        (TRANSPORT_DATA_ENDPOINT_PATH, BulkDatasetId.TRANSPORT),
        (MSS_DATA_ENDPOINT_PATH, BulkDatasetId.MSS),
        (COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.CA),
        (SWELLING_DATA_ENDPOINT_PATH, BulkDatasetId.SWELLING),
        (CVD_DATA_ENDPOINT_PATH, BulkDatasetId.CVD),
        (STO_DATA_ENDPOINT_PATH, BulkDatasetId.STO),
        (WATERANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.WA),
        (INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, BulkDatasetId.IT),
        (VLE_DATA_ENDPOINT_PATH, BulkDatasetId.VLE),
        (MCM_DATA_ENDPOINT_PATH, BulkDatasetId.MCM),
        (SLIMTUBE_DATA_ENDPOINT_PATH, BulkDatasetId.SLIMTUBE),
        (RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, BulkDatasetId.RELATIVE_PERMEABILITY),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH, BulkDatasetId.CAP_PRESSURE),
        (FRACTIONATION_DATA_ENDPOINT_PATH, BulkDatasetId.FRACTIONATION),
        (EXTRACTION_DATA_ENDPOINT_PATH, BulkDatasetId.EXTRACTION),
        (PHYS_CHEM_DATA_ENDPOINT_PATH, BulkDatasetId.PHYS_CHEM),
        (WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH, BulkDatasetId.WATER_GAS_RELATIVE_PERMEABILITY),
        (ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, BulkDatasetId.ROCK_COMPRESSIBILITY),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH, BulkDatasetId.ELECTRICAL_PROPERTIES),
        (FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH, BulkDatasetId.FORMATION_RESISTIVITY_INDEX),
        (NMR_DATA_ENDPOINT_PATH, BulkDatasetId.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH, BulkDatasetId.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH, BulkDatasetId.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_RATIOS),
        (WHOLE_OIL_GC_DATA_ENDPOINT_PATH, BulkDatasetId.WHOLE_OIL_GC),
    ],
)
@pytest.mark.asyncio
async def test_get_rca_data_no_content_header(data_endpoint_path, dataset_id, with_patched_storage_get_success_200):
    with get_overrides():
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
        (RCA_DATA_ENDPOINT_PATH, BulkDatasetId.RCA),
        (CCE_DATA_ENDPOINT_PATH, BulkDatasetId.CCE),
        (DIF_LIB_DATA_ENDPOINT_PATH, BulkDatasetId.DIF_LIB),
        (TRANSPORT_DATA_ENDPOINT_PATH, BulkDatasetId.TRANSPORT),
        (MSS_DATA_ENDPOINT_PATH, BulkDatasetId.MSS),
        (COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.CA),
        (SWELLING_DATA_ENDPOINT_PATH, BulkDatasetId.SWELLING),
        (CVD_DATA_ENDPOINT_PATH, BulkDatasetId.CVD),
        (STO_DATA_ENDPOINT_PATH, BulkDatasetId.STO),
        (WATERANALYSIS_DATA_ENDPOINT_PATH, BulkDatasetId.WA),
        (INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, BulkDatasetId.IT),
        (VLE_DATA_ENDPOINT_PATH, BulkDatasetId.VLE),
        (MCM_DATA_ENDPOINT_PATH, BulkDatasetId.MCM),
        (SLIMTUBE_DATA_ENDPOINT_PATH, BulkDatasetId.SLIMTUBE),
        (RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, BulkDatasetId.RELATIVE_PERMEABILITY),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH, BulkDatasetId.CAP_PRESSURE),
        (FRACTIONATION_DATA_ENDPOINT_PATH, BulkDatasetId.FRACTIONATION),
        (EXTRACTION_DATA_ENDPOINT_PATH, BulkDatasetId.EXTRACTION),
        (PHYS_CHEM_DATA_ENDPOINT_PATH, BulkDatasetId.PHYS_CHEM),
        (WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH, BulkDatasetId.WATER_GAS_RELATIVE_PERMEABILITY),
        (ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, BulkDatasetId.ROCK_COMPRESSIBILITY),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH, BulkDatasetId.ELECTRICAL_PROPERTIES),
        (FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH, BulkDatasetId.FORMATION_RESISTIVITY_INDEX),
        (NMR_DATA_ENDPOINT_PATH, BulkDatasetId.NMR),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH, BulkDatasetId.MULTIPLE_SALINITY),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_ALKANES),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH, BulkDatasetId.MERCURY_INJECTION),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_AROMATICS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH, BulkDatasetId.GCMS_RATIOS),
        (WHOLE_OIL_GC_DATA_ENDPOINT_PATH, BulkDatasetId.WHOLE_OIL_GC),
    ],
)
@pytest.mark.asyncio
async def test_get_rca_data_wrong_content_header(data_endpoint_path, dataset_id, with_patched_storage_get_success_200):
    with get_overrides():
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
            RCA_DATA_ENDPOINT_PATH, data_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            CCE_DATA_ENDPOINT_PATH, cce_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH, dif_lib_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH, transport_test_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            MSS_DATA_ENDPOINT_PATH, mss_test_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH, swelling_test_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            CVD_DATA_ENDPOINT_PATH, cvd_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            STO_DATA_ENDPOINT_PATH, sto_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH, water_analysis_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            VLE_DATA_ENDPOINT_PATH, vle_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            MCM_DATA_ENDPOINT_PATH, mcm_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH, slimtubetest_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, relative_permeability_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH, cappressure_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH, fractionation_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH, extraction_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH, physchem_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID, "get_record", [
                rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ], "download_file", [build_get_test_data("x-parquet")],
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet")],
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet")],
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
            "get_record",
            [
                whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            ],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
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
    with get_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                f"{data_endpoint_path}/{dataset_id}",
                headers=TEST_HEADERS_PARQUET,
            )
    arrow_table = pq.read_table(pa.BufferReader(blobs[0]))
    assert response.status_code == status.HTTP_200_OK
    assert pq.read_table(pa.BufferReader(response.content)).equals(arrow_table)


@pytest.mark.parametrize(
    "data_endpoint_path,params,returned_data_reasons", [
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            data_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            rock_compressibility_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_COLUMNS_FILTERS[0],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[0],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_COLUMNS_FILTERS[1],
            TEST_WRONG_COLUMNS_FILTERS_REASONS[1],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_ROWS_FILTERS[0],
            TEST_WRONG_ROWS_FILTERS_REASONS[0],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_ROWS_FILTERS[1],
            TEST_WRONG_ROWS_FILTERS_REASONS[1],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_ROWS_FILTERS[2],
            TEST_WRONG_ROWS_FILTERS_REASONS[2],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_AGGREGATION[0],
            TEST_WRONG_AGGREGATION_REASONS[0],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_AGGREGATION[1],
            TEST_WRONG_AGGREGATION_REASONS[1],
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_WRONG_AGGREGATION[2],
            TEST_WRONG_AGGREGATION_REASONS[2],
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_rca_data_json_data_errors(data_endpoint_path, params, returned_data_reasons):
    with get_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(
                data_endpoint_path,
                headers=TEST_HEADERS_JSON,
                params=params,
            )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert re.match(returned_data_reasons, response.json()["reason"])


@pytest.mark.parametrize(
    "data_endpoint_path,params,storage_method,osdu_records,dataset_method,blobs,returned_data", [
        (
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", TEST_DATA)],
            TEST_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_DATA,
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", formationresistivityindex_mock_objects.TEST_DATA)],
            formationresistivityindex_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            None,
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            cce_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", extraction_mock_objects.TEST_DATA)],
            extraction_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects.TEST_DATA)],
            electricalproperties_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            nmr_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            multiple_salinity_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_alkanes_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            mercuryinjection_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_aromatics_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_ratios_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            whole_oil_gc_mock_objects.TEST_PARAMS_AGGREGATION,
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_AGGREGATED_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            cce_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            dif_lib_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            transport_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            mss_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            compositionalanalysis_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            swelling_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            cvd_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            sto_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            water_analysis_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            interfacialtension_test_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            vle_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            mcm_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            slimtubetest_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            relative_permeability_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            extraction_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", extraction_mock_objects.TEST_DATA)],
            extraction_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            electricalproperties_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects.TEST_DATA)],
            electricalproperties_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            cappressure_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            fractionation_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            physchem_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", physchem_mock_objects.TEST_DATA)],
            physchem_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            water_gas_rel_perm_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_gas_rel_perm_mock_objects.TEST_DATA)],
            water_gas_rel_perm_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            formationresistivityindex_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", formationresistivityindex_mock_objects.TEST_DATA)],
            formationresistivityindex_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            nmr_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            multiple_salinity_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_alkanes_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            mercuryinjection_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_aromatics_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            gcms_ratios_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_FILTERED_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            whole_oil_gc_mock_objects.TEST_PARAMS_FILTERS,
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_FILTERED_DATA,
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
    with get_overrides():
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
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", TEST_DATA)],
            TEST_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_DATA,
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", extraction_mock_objects.TEST_DATA)],
            extraction_mock_objects.TEST_DATA,
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", physchem_mock_objects.TEST_DATA)],
            physchem_mock_objects.TEST_DATA,
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_gas_rel_perm_mock_objects.TEST_DATA)],
            water_gas_rel_perm_mock_objects.TEST_DATA,
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rock_compressibility_mock_objects.TEST_DATA)],
            rock_compressibility_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects.TEST_DATA)],
            electricalproperties_mock_objects.TEST_DATA,
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", formationresistivityindex_mock_objects.TEST_DATA)],
            formationresistivityindex_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_DATA,
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
    with get_overrides():
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
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", TEST_DATA)],
            TEST_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_DATA,
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", extraction_mock_objects.TEST_DATA)],
            extraction_mock_objects.TEST_DATA,
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", physchem_mock_objects.TEST_DATA)],
            physchem_mock_objects.TEST_DATA,
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_gas_rel_perm_mock_objects.TEST_DATA)],
            water_gas_rel_perm_mock_objects.TEST_DATA,
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rock_compressibility_mock_objects.TEST_DATA)],
            rock_compressibility_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects.TEST_DATA)],
            electricalproperties_mock_objects.TEST_DATA,
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", formationresistivityindex_mock_objects.TEST_DATA)],
            formationresistivityindex_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_DATA,
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
    with get_overrides():
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
            f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [data_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", TEST_DATA)],
            TEST_DATA,
        ),
        (
            f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cce_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cce_mock_objects.TEST_DATA)],
            cce_mock_objects.TEST_DATA,
        ),
        (
            f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [dif_lib_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", dif_lib_mock_objects.TEST_DATA)],
            dif_lib_mock_objects.TEST_DATA,
        ),
        (
            f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [transport_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", transport_test_mock_objects.TEST_DATA)],
            transport_test_mock_objects.TEST_DATA,
        ),
        (
            f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mss_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mss_test_mock_objects.TEST_DATA)],
            mss_test_mock_objects.TEST_DATA,
        ),
        (
            f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [compositionalanalysis_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", compositionalanalysis_mock_objects.TEST_DATA)],
            compositionalanalysis_mock_objects.TEST_DATA,
        ),
        (
            f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [swelling_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", swelling_test_mock_objects.TEST_DATA)],
            swelling_test_mock_objects.TEST_DATA,
        ),
        (
            f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cvd_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cvd_mock_objects.TEST_DATA)],
            cvd_mock_objects.TEST_DATA,
        ),
        (
            f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [sto_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", sto_mock_objects.TEST_DATA)],
            sto_mock_objects.TEST_DATA,
        ),
        (
            f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_analysis_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_analysis_mock_objects.TEST_DATA)],
            water_analysis_mock_objects.TEST_DATA,
        ),
        (
            f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [interfacialtension_test_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", interfacialtension_test_mock_objects.TEST_DATA)],
            interfacialtension_test_mock_objects.TEST_DATA,
        ),
        (
            f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [vle_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", vle_mock_objects.TEST_DATA)],
            vle_mock_objects.TEST_DATA,
        ),
        (
            f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mcm_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mcm_mock_objects.TEST_DATA)],
            mcm_mock_objects.TEST_DATA,
        ),
        (
            f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [slimtubetest_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", slimtubetest_mock_objects.TEST_DATA)],
            slimtubetest_mock_objects.TEST_DATA,
        ),
        (
            f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [relative_permeability_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", relative_permeability_mock_objects.TEST_DATA)],
            relative_permeability_mock_objects.TEST_DATA,
        ),
        (
            f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [cappressure_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", cappressure_mock_objects.TEST_DATA)],
            cappressure_mock_objects.TEST_DATA,
        ),
        (
            f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [fractionation_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", fractionation_mock_objects.TEST_DATA)],
            fractionation_mock_objects.TEST_DATA,
        ),
        (
            f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [extraction_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", extraction_mock_objects.TEST_DATA)],
            extraction_mock_objects.TEST_DATA,
        ),
        (
            f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [physchem_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", physchem_mock_objects.TEST_DATA)],
            physchem_mock_objects.TEST_DATA,
        ),
        (
            f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", water_gas_rel_perm_mock_objects.TEST_DATA)],
            water_gas_rel_perm_mock_objects.TEST_DATA,
        ),
        (
            f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [rock_compressibility_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", rock_compressibility_mock_objects.TEST_DATA)],
            rock_compressibility_mock_objects.TEST_DATA,
        ),
        (
            f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [electricalproperties_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", electricalproperties_mock_objects.TEST_DATA)],
            electricalproperties_mock_objects.TEST_DATA,
        ),
        (
            f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [formationresistivityindex_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", formationresistivityindex_mock_objects.TEST_DATA)],
            formationresistivityindex_mock_objects.TEST_DATA,
        ),
        (
            f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [nmr_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", nmr_mock_objects.TEST_DATA)],
            nmr_mock_objects.TEST_DATA,
        ),
        (
            f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [multiple_salinity_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", multiple_salinity_mock_objects.TEST_DATA)],
            multiple_salinity_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_alkanes_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_alkanes_mock_objects.TEST_DATA)],
            gcms_alkanes_mock_objects.TEST_DATA,
        ),
        (
            f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [mercuryinjection_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", mercuryinjection_mock_objects.TEST_DATA)],
            mercuryinjection_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_aromatics_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_aromatics_mock_objects.TEST_DATA)],
            gcms_aromatics_mock_objects.TEST_DATA,
        ),
        (
            f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [gcms_ratios_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", gcms_ratios_mock_objects.TEST_DATA)],
            gcms_ratios_mock_objects.TEST_DATA,
        ),
        (
            f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
            "get_record",
            [whole_oil_gc_mock_objects.RECORD_DATA_WITH_IMPROPER_SCHEMA_VERSION],
            "download_file",
            [build_get_test_data("x-parquet", whole_oil_gc_mock_objects.TEST_DATA)],
            whole_oil_gc_mock_objects.TEST_DATA,
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
    with get_overrides():
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
            RCA_DATA_ENDPOINT_PATH,
            data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            TEST_DATA,
            data_mock_objects.TEST_DATASET_RECORD_ID,
            data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CCE_DATA_ENDPOINT_PATH,
            cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cce_mock_objects.TEST_DATA,
            cce_mock_objects.TEST_DATASET_RECORD_ID,
            cce_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            dif_lib_mock_objects.TEST_DATA,
            dif_lib_mock_objects.TEST_DATASET_RECORD_ID,
            dif_lib_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            transport_test_mock_objects.TEST_DATA,
            transport_test_mock_objects.TEST_DATASET_RECORD_ID,
            transport_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mss_test_mock_objects.TEST_DATA,
            mss_test_mock_objects.TEST_DATASET_RECORD_ID,
            mss_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            compositionalanalysis_mock_objects.TEST_DATA,
            compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID,
            compositionalanalysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            swelling_test_mock_objects.TEST_DATA,
            swelling_test_mock_objects.TEST_DATASET_RECORD_ID,
            swelling_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cvd_mock_objects.TEST_DATA,
            cvd_mock_objects.TEST_DATASET_RECORD_ID,
            cvd_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            sto_mock_objects.TEST_DATA,
            sto_mock_objects.TEST_DATASET_RECORD_ID,
            sto_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_analysis_mock_objects.TEST_DATA,
            water_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            water_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            interfacialtension_test_mock_objects.TEST_DATA,
            interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID,
            interfacialtension_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            vle_mock_objects.TEST_DATA,
            vle_mock_objects.TEST_DATASET_RECORD_ID,
            vle_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mcm_mock_objects.TEST_DATA,
            mcm_mock_objects.TEST_DATASET_RECORD_ID,
            mcm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            slimtubetest_mock_objects.TEST_DATA,
            slimtubetest_mock_objects.TEST_DATASET_RECORD_ID,
            slimtubetest_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            relative_permeability_mock_objects.TEST_DATA,
            relative_permeability_mock_objects.TEST_DATASET_RECORD_ID,
            relative_permeability_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            fractionation_mock_objects.TEST_DATA,
            fractionation_mock_objects.TEST_DATASET_RECORD_ID,
            fractionation_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            extraction_mock_objects.TEST_DATA,
            extraction_mock_objects.TEST_DATASET_RECORD_ID,
            extraction_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            physchem_mock_objects.TEST_DATA,
            physchem_mock_objects.TEST_DATASET_RECORD_ID,
            physchem_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_gas_rel_perm_mock_objects.TEST_DATA,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID,
            water_gas_rel_perm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rock_compressibility_mock_objects.TEST_DATA,
            rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID,
            rock_compressibility_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects.TEST_DATA,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            formationresistivityindex_mock_objects.TEST_DATA,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
            formationresistivityindex_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            whole_oil_gc_mock_objects.TEST_DATA,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
            whole_oil_gc_mock_objects.TEST_DDMS_URN_WITH_VERSION,
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
            RCA_DATA_ENDPOINT_PATH,
            data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            TEST_DATA,
            data_mock_objects.TEST_DATASET_RECORD_ID,
            data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CCE_DATA_ENDPOINT_PATH,
            cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cce_mock_objects.TEST_DATA,
            cce_mock_objects.TEST_DATASET_RECORD_ID,
            cce_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            dif_lib_mock_objects.TEST_DATA,
            dif_lib_mock_objects.TEST_DATASET_RECORD_ID,
            dif_lib_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            transport_test_mock_objects.TEST_DATA,
            transport_test_mock_objects.TEST_DATASET_RECORD_ID,
            transport_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mss_test_mock_objects.TEST_DATA,
            mss_test_mock_objects.TEST_DATASET_RECORD_ID,
            mss_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            compositionalanalysis_mock_objects.TEST_DATA,
            compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID,
            compositionalanalysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            swelling_test_mock_objects.TEST_DATA,
            swelling_test_mock_objects.TEST_DATASET_RECORD_ID,
            swelling_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cvd_mock_objects.TEST_DATA,
            cvd_mock_objects.TEST_DATASET_RECORD_ID,
            cvd_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            sto_mock_objects.TEST_DATA,
            sto_mock_objects.TEST_DATASET_RECORD_ID,
            sto_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_analysis_mock_objects.TEST_DATA,
            water_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            water_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            interfacialtension_test_mock_objects.TEST_DATA,
            interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID,
            interfacialtension_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            vle_mock_objects.TEST_DATA,
            vle_mock_objects.TEST_DATASET_RECORD_ID,
            vle_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mcm_mock_objects.TEST_DATA,
            mcm_mock_objects.TEST_DATASET_RECORD_ID,
            mcm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            slimtubetest_mock_objects.TEST_DATA,
            slimtubetest_mock_objects.TEST_DATASET_RECORD_ID,
            slimtubetest_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            relative_permeability_mock_objects.TEST_DATA,
            relative_permeability_mock_objects.TEST_DATASET_RECORD_ID,
            relative_permeability_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            fractionation_mock_objects.TEST_DATA,
            fractionation_mock_objects.TEST_DATASET_RECORD_ID,
            fractionation_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            extraction_mock_objects.TEST_DATA,
            extraction_mock_objects.TEST_DATASET_RECORD_ID,
            extraction_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            physchem_mock_objects.TEST_DATA,
            physchem_mock_objects.TEST_DATASET_RECORD_ID,
            physchem_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_gas_rel_perm_mock_objects.TEST_DATA,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID,
            water_gas_rel_perm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rock_compressibility_mock_objects.TEST_DATA,
            rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID,
            rock_compressibility_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects.TEST_DATA,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            formationresistivityindex_mock_objects.TEST_DATA,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
            formationresistivityindex_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            whole_oil_gc_mock_objects.TEST_DATA,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
            whole_oil_gc_mock_objects.TEST_DDMS_URN_WITH_VERSION,
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
            RCA_DATA_ENDPOINT_PATH,
            data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            data_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CCE_DATA_ENDPOINT_PATH,
            cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cce_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            dif_lib_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            transport_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mss_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            swelling_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cvd_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            sto_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_analysis_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            vle_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mcm_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            slimtubetest_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            relative_permeability_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            fractionation_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            extraction_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            physchem_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
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
            RCA_DATA_ENDPOINT_PATH,
            data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            TEST_DATA,
            data_mock_objects.TEST_DATASET_RECORD_ID,
            data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CCE_DATA_ENDPOINT_PATH,
            cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cce_mock_objects.TEST_DATA,
            cce_mock_objects.TEST_DATASET_RECORD_ID,
            cce_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            dif_lib_mock_objects.TEST_DATA,
            dif_lib_mock_objects.TEST_DATASET_RECORD_ID,
            dif_lib_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            transport_test_mock_objects.TEST_DATA,
            transport_test_mock_objects.TEST_DATASET_RECORD_ID,
            transport_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mss_test_mock_objects.TEST_DATA,
            mss_test_mock_objects.TEST_DATASET_RECORD_ID,
            mss_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            compositionalanalysis_mock_objects.TEST_DATA,
            compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID,
            compositionalanalysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            swelling_test_mock_objects.TEST_DATA,
            swelling_test_mock_objects.TEST_DATASET_RECORD_ID,
            swelling_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cvd_mock_objects.TEST_DATA,
            cvd_mock_objects.TEST_DATASET_RECORD_ID,
            cvd_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            sto_mock_objects.TEST_DATA,
            sto_mock_objects.TEST_DATASET_RECORD_ID,
            sto_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_analysis_mock_objects.TEST_DATA,
            water_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            water_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            interfacialtension_test_mock_objects.TEST_DATA,
            interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID,
            interfacialtension_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            vle_mock_objects.TEST_DATA,
            vle_mock_objects.TEST_DATASET_RECORD_ID,
            vle_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mcm_mock_objects.TEST_DATA,
            mcm_mock_objects.TEST_DATASET_RECORD_ID,
            mcm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            slimtubetest_mock_objects.TEST_DATA,
            slimtubetest_mock_objects.TEST_DATASET_RECORD_ID,
            slimtubetest_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            relative_permeability_mock_objects.TEST_DATA,
            relative_permeability_mock_objects.TEST_DATASET_RECORD_ID,
            relative_permeability_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            fractionation_mock_objects.TEST_DATA,
            fractionation_mock_objects.TEST_DATASET_RECORD_ID,
            fractionation_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            extraction_mock_objects.TEST_DATA,
            extraction_mock_objects.TEST_DATASET_RECORD_ID,
            extraction_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            physchem_mock_objects.TEST_DATA,
            physchem_mock_objects.TEST_DATASET_RECORD_ID,
            physchem_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_gas_rel_perm_mock_objects.TEST_DATA,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID,
            water_gas_rel_perm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rock_compressibility_mock_objects.TEST_DATA,
            rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID,
            rock_compressibility_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects.TEST_DATA,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            formationresistivityindex_mock_objects.TEST_DATA,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
            formationresistivityindex_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            whole_oil_gc_mock_objects.TEST_DATA,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
            whole_oil_gc_mock_objects.TEST_DDMS_URN_WITH_VERSION,
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
            RCA_DATA_ENDPOINT_PATH,
            data_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            TEST_DATA,
            data_mock_objects.TEST_DATASET_RECORD_ID,
            data_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CCE_DATA_ENDPOINT_PATH,
            cce_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cce_mock_objects.TEST_DATA,
            cce_mock_objects.TEST_DATASET_RECORD_ID,
            cce_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            dif_lib_mock_objects.TEST_DATA,
            dif_lib_mock_objects.TEST_DATASET_RECORD_ID,
            dif_lib_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            transport_test_mock_objects.TEST_DATA,
            transport_test_mock_objects.TEST_DATASET_RECORD_ID,
            transport_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mss_test_mock_objects.TEST_DATA,
            mss_test_mock_objects.TEST_DATASET_RECORD_ID,
            mss_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            compositionalanalysis_mock_objects.TEST_DATA,
            compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID,
            compositionalanalysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            swelling_test_mock_objects.TEST_DATA,
            swelling_test_mock_objects.TEST_DATASET_RECORD_ID,
            swelling_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cvd_mock_objects.TEST_DATA,
            cvd_mock_objects.TEST_DATASET_RECORD_ID,
            cvd_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            sto_mock_objects.TEST_DATA,
            sto_mock_objects.TEST_DATASET_RECORD_ID,
            sto_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_analysis_mock_objects.TEST_DATA,
            water_analysis_mock_objects.TEST_DATASET_RECORD_ID,
            water_analysis_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            interfacialtension_test_mock_objects.TEST_DATA,
            interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID,
            interfacialtension_test_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            vle_mock_objects.TEST_DATA,
            vle_mock_objects.TEST_DATASET_RECORD_ID,
            vle_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mcm_mock_objects.TEST_DATA,
            mcm_mock_objects.TEST_DATASET_RECORD_ID,
            mcm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            slimtubetest_mock_objects.TEST_DATA,
            slimtubetest_mock_objects.TEST_DATASET_RECORD_ID,
            slimtubetest_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            relative_permeability_mock_objects.TEST_DATA,
            relative_permeability_mock_objects.TEST_DATASET_RECORD_ID,
            relative_permeability_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            cappressure_mock_objects.TEST_DATA,
            cappressure_mock_objects.TEST_DATASET_RECORD_ID,
            cappressure_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            fractionation_mock_objects.TEST_DATA,
            fractionation_mock_objects.TEST_DATASET_RECORD_ID,
            fractionation_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            extraction_mock_objects.TEST_DATA,
            extraction_mock_objects.TEST_DATASET_RECORD_ID,
            extraction_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            physchem_mock_objects.TEST_DATA,
            physchem_mock_objects.TEST_DATASET_RECORD_ID,
            physchem_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            water_gas_rel_perm_mock_objects.TEST_DATA,
            water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID,
            water_gas_rel_perm_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            rock_compressibility_mock_objects.TEST_DATA,
            rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID,
            rock_compressibility_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            electricalproperties_mock_objects.TEST_DATA,
            electricalproperties_mock_objects.TEST_DATASET_RECORD_ID,
            electricalproperties_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            formationresistivityindex_mock_objects.TEST_DATA,
            formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID,
            formationresistivityindex_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            nmr_mock_objects.TEST_DATA,
            nmr_mock_objects.TEST_DATASET_RECORD_ID,
            nmr_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            multiple_salinity_mock_objects.TEST_DATA,
            multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID,
            multiple_salinity_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_alkanes_mock_objects.TEST_DATA,
            gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_alkanes_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            mercuryinjection_mock_objects.TEST_DATA,
            mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID,
            mercuryinjection_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_aromatics_mock_objects.TEST_DATA,
            gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_aromatics_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            gcms_ratios_mock_objects.TEST_DATA,
            gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID,
            gcms_ratios_mock_objects.TEST_DDMS_URN_WITH_VERSION,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.RECORD_DATA_WITH_SCHEMA_VERSION,
            whole_oil_gc_mock_objects.TEST_DATA,
            whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID,
            whole_oil_gc_mock_objects.TEST_DDMS_URN_WITH_VERSION,
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
        (RCA_DATA_ENDPOINT_PATH, data_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CCE_DATA_ENDPOINT_PATH, cce_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (DIF_LIB_DATA_ENDPOINT_PATH, dif_lib_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (TRANSPORT_DATA_ENDPOINT_PATH, transport_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MSS_DATA_ENDPOINT_PATH, mss_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, compositionalanalysis_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (SWELLING_DATA_ENDPOINT_PATH, swelling_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CVD_DATA_ENDPOINT_PATH, cvd_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (STO_DATA_ENDPOINT_PATH, sto_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (WATERANALYSIS_DATA_ENDPOINT_PATH, water_analysis_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, interfacialtension_test_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (VLE_DATA_ENDPOINT_PATH, vle_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MCM_DATA_ENDPOINT_PATH, mcm_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (SLIMTUBE_DATA_ENDPOINT_PATH, slimtubetest_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, relative_permeability_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH, cappressure_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (FRACTIONATION_DATA_ENDPOINT_PATH, fractionation_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (EXTRACTION_DATA_ENDPOINT_PATH, extraction_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (PHYS_CHEM_DATA_ENDPOINT_PATH, physchem_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH, water_gas_rel_perm_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, rock_compressibility_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH, electricalproperties_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.INCORRECT_SCHEMA_TEST_DATA,
        ),
        (NMR_DATA_ENDPOINT_PATH, nmr_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH, multiple_salinity_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH, gcms_alkanes_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH, mercuryinjection_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH, gcms_aromatics_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH, gcms_ratios_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
        (WHOLE_OIL_GC_DATA_ENDPOINT_PATH, whole_oil_gc_mock_objects.INCORRECT_SCHEMA_TEST_DATA),
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
        (RCA_DATA_ENDPOINT_PATH, data_mock_objects.INCORRECT_DATAFRAME_TEST_DATA, data_mock_objects.EXPECTED_ERROR_REASON),
        (CCE_DATA_ENDPOINT_PATH, cce_mock_objects.INCORRECT_DATAFRAME_TEST_DATA, cce_mock_objects.EXPECTED_ERROR_REASON),
        (
            DIF_LIB_DATA_ENDPOINT_PATH,
            dif_lib_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            dif_lib_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            TRANSPORT_DATA_ENDPOINT_PATH,
            transport_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            transport_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MSS_DATA_ENDPOINT_PATH,
            mss_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            mss_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
            compositionalanalysis_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            compositionalanalysis_mock_objects.EXPECTED_ERROR_REASON,
        ),

        (
            SWELLING_DATA_ENDPOINT_PATH,
            swelling_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            swelling_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            CVD_DATA_ENDPOINT_PATH,
            cvd_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            cvd_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            STO_DATA_ENDPOINT_PATH,
            sto_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            sto_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            WATERANALYSIS_DATA_ENDPOINT_PATH,
            water_analysis_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            water_analysis_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
            interfacialtension_test_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            interfacialtension_test_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            VLE_DATA_ENDPOINT_PATH,
            vle_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            vle_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MCM_DATA_ENDPOINT_PATH,
            mcm_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            mcm_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            SLIMTUBE_DATA_ENDPOINT_PATH,
            slimtubetest_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            slimtubetest_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
            relative_permeability_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            relative_permeability_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            CAP_PRESSURE_DATA_ENDPOINT_PATH,
            cappressure_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            cappressure_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            FRACTIONATION_DATA_ENDPOINT_PATH,
            fractionation_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            fractionation_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            EXTRACTION_DATA_ENDPOINT_PATH,
            extraction_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            extraction_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            PHYS_CHEM_DATA_ENDPOINT_PATH,
            physchem_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            physchem_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
            water_gas_rel_perm_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            water_gas_rel_perm_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
            rock_compressibility_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            rock_compressibility_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
            electricalproperties_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            electricalproperties_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
            formationresistivityindex_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            formationresistivityindex_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            NMR_DATA_ENDPOINT_PATH,
            nmr_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            nmr_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
            multiple_salinity_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            multiple_salinity_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_ALKANES_DATA_ENDPOINT_PATH,
            gcms_alkanes_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_alkanes_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            MERCURY_INJECTION_DATA_ENDPOINT_PATH,
            mercuryinjection_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            mercuryinjection_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_AROMATICS_DATA_ENDPOINT_PATH,
            gcms_aromatics_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_aromatics_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            GCMS_RATIOS_DATA_ENDPOINT_PATH,
            gcms_ratios_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            gcms_ratios_mock_objects.EXPECTED_ERROR_REASON,
        ),
        (
            WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
            whole_oil_gc_mock_objects.INCORRECT_DATAFRAME_TEST_DATA,
            whole_oil_gc_mock_objects.EXPECTED_ERROR_REASON,

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
        f"{RCA_DATA_ENDPOINT_PATH}/{data_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CCE_DATA_ENDPOINT_PATH}/{cce_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{DIF_LIB_DATA_ENDPOINT_PATH}/{dif_lib_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{TRANSPORT_DATA_ENDPOINT_PATH}/{transport_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MSS_DATA_ENDPOINT_PATH}/{mss_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH}/{compositionalanalysis_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{SWELLING_DATA_ENDPOINT_PATH}/{swelling_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CVD_DATA_ENDPOINT_PATH}/{cvd_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{STO_DATA_ENDPOINT_PATH}/{sto_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{WATERANALYSIS_DATA_ENDPOINT_PATH}/{water_analysis_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{INTERFACIAL_TENSION_DATA_ENDPOINT_PATH}/{interfacialtension_test_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{VLE_DATA_ENDPOINT_PATH}/{vle_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MCM_DATA_ENDPOINT_PATH}/{mcm_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{SLIMTUBE_DATA_ENDPOINT_PATH}/{slimtubetest_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH}/{relative_permeability_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{CAP_PRESSURE_DATA_ENDPOINT_PATH}/{cappressure_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{FRACTIONATION_DATA_ENDPOINT_PATH}/{fractionation_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{EXTRACTION_DATA_ENDPOINT_PATH}/{extraction_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{PHYS_CHEM_DATA_ENDPOINT_PATH}/{physchem_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH}/{water_gas_rel_perm_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH}/{rock_compressibility_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH}/{electricalproperties_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH}/{formationresistivityindex_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{NMR_DATA_ENDPOINT_PATH}/{nmr_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MULTIPLE_SALINITY_DATA_ENDPOINT_PATH}/{multiple_salinity_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_ALKANES_DATA_ENDPOINT_PATH}/{gcms_alkanes_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{MERCURY_INJECTION_DATA_ENDPOINT_PATH}/{mercuryinjection_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_AROMATICS_DATA_ENDPOINT_PATH}/{gcms_aromatics_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{GCMS_RATIOS_DATA_ENDPOINT_PATH}/{gcms_ratios_mock_objects.TEST_DATASET_RECORD_ID}",
        f"{WHOLE_OIL_GC_DATA_ENDPOINT_PATH}/{whole_oil_gc_mock_objects.TEST_DATASET_RECORD_ID}",
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
        RCA_DATA_ENDPOINT_PATH,
        CCE_DATA_ENDPOINT_PATH,
        DIF_LIB_DATA_ENDPOINT_PATH,
        TRANSPORT_DATA_ENDPOINT_PATH,
        MSS_DATA_ENDPOINT_PATH,
        COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
        SWELLING_DATA_ENDPOINT_PATH,
        CVD_DATA_ENDPOINT_PATH,
        STO_DATA_ENDPOINT_PATH,
        WATERANALYSIS_DATA_ENDPOINT_PATH,
        INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
        VLE_DATA_ENDPOINT_PATH,
        MCM_DATA_ENDPOINT_PATH,
        SLIMTUBE_DATA_ENDPOINT_PATH,
        RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
        CAP_PRESSURE_DATA_ENDPOINT_PATH,
        FRACTIONATION_DATA_ENDPOINT_PATH,
        EXTRACTION_DATA_ENDPOINT_PATH,
        PHYS_CHEM_DATA_ENDPOINT_PATH,
        WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
        ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
        ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
        FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
        NMR_DATA_ENDPOINT_PATH,
        MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
        GCMS_ALKANES_DATA_ENDPOINT_PATH,
        MERCURY_INJECTION_DATA_ENDPOINT_PATH,
        GCMS_AROMATICS_DATA_ENDPOINT_PATH,
        GCMS_RATIOS_DATA_ENDPOINT_PATH,
        WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
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
    "data_endpoint_path,integrity_error_dataframe_data", [
        (RCA_DATA_ENDPOINT_PATH, data_mock_objects.INTEGRITY_ERROR_DATAFRAME_DATA),
    ],
)
@pytest.mark.asyncio
async def test_post_rca_integrity_error(data_endpoint_path, integrity_error_dataframe_data):
    with post_overrides():
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
    assert isinstance(errors, dict)
    assert len(errors) == 1
    assert set(errors.keys()) == {"Missing records in storage"}
    assert len(errors["Missing records in storage"]) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        RCA_DATA_ENDPOINT_PATH,
        CCE_DATA_ENDPOINT_PATH,
        DIF_LIB_DATA_ENDPOINT_PATH,
        TRANSPORT_DATA_ENDPOINT_PATH,
        MSS_DATA_ENDPOINT_PATH,
        COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH,
        SWELLING_DATA_ENDPOINT_PATH,
        CVD_DATA_ENDPOINT_PATH,
        STO_DATA_ENDPOINT_PATH,
        WATERANALYSIS_DATA_ENDPOINT_PATH,
        INTERFACIAL_TENSION_DATA_ENDPOINT_PATH,
        VLE_DATA_ENDPOINT_PATH,
        MCM_DATA_ENDPOINT_PATH,
        SLIMTUBE_DATA_ENDPOINT_PATH,
        RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH,
        CAP_PRESSURE_DATA_ENDPOINT_PATH,
        FRACTIONATION_DATA_ENDPOINT_PATH,
        EXTRACTION_DATA_ENDPOINT_PATH,
        PHYS_CHEM_DATA_ENDPOINT_PATH,
        WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH,
        ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH,
        ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH,
        FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH,
        NMR_DATA_ENDPOINT_PATH,
        MULTIPLE_SALINITY_DATA_ENDPOINT_PATH,
        GCMS_ALKANES_DATA_ENDPOINT_PATH,
        MERCURY_INJECTION_DATA_ENDPOINT_PATH,
        GCMS_AROMATICS_DATA_ENDPOINT_PATH,
        GCMS_RATIOS_DATA_ENDPOINT_PATH,
        WHOLE_OIL_GC_DATA_ENDPOINT_PATH,
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
        (RCA_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (CCE_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (DIF_LIB_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (TRANSPORT_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (MSS_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (SWELLING_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (CVD_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (STO_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (WATERANALYSIS_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (INTERFACIAL_TENSION_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (VLE_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (MCM_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (SLIMTUBE_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (CAP_PRESSURE_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (FRACTIONATION_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (EXTRACTION_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (PHYS_CHEM_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (NMR_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (MULTIPLE_SALINITY_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_ALKANES_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (MERCURY_INJECTION_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_AROMATICS_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (GCMS_RATIOS_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
        (WHOLE_OIL_GC_DATA_ENDPOINT_PATH, ORIENT_SPLIT_400_PAYLOADS),
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


# Download Source section #
#####################

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,storage_method,osdu_records,dataset_method,blobs",
    [
        (
            RCA_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            RCA_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            RCA_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            PVT_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            PVT_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            PVT_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            CCE_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            CCE_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            CCE_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            DIF_LIB_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            DIF_LIB_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            DIF_LIB_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            TRANSPORT_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            TRANSPORT_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            TRANSPORT_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            MSS_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            MSS_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            MSS_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            COMPOSITIONALANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            COMPOSITIONALANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            COMPOSITIONALANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            SWELLING_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            SWELLING_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            SWELLING_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            CVD_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            CVD_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            CVD_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            STO_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            STO_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            STO_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            WATERANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            WATERANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            WATERANALYSIS_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            INTERFACIAL_TENSION_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            INTERFACIAL_TENSION_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            INTERFACIAL_TENSION_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            VLE_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            VLE_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            VLE_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            MCM_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            MCM_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            MCM_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            SLIMTUBE_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            SLIMTUBE_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            SLIMTUBE_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            RELATIVE_PERMEABILITY_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            RELATIVE_PERMEABILITY_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            RELATIVE_PERMEABILITY_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            FRACTIONATION_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            FRACTIONATION_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            FRACTIONATION_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            EXTRACTION_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            EXTRACTION_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            EXTRACTION_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            PHYS_CHEM_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            PHYS_CHEM_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            PHYS_CHEM_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            WATER_GAS_REL_PERM_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            WATER_GAS_REL_PERM_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            WATER_GAS_REL_PERM_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            ELECTRICAL_PROPERTIES_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            ELECTRICAL_PROPERTIES_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            ELECTRICAL_PROPERTIES_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_SOURCE_ENDPOINT_PATH,
            "get_record",
            MULTIPLE_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            MULTIPLE_DATASETS_DATASET_SIDE_EFFECT,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_SOURCE_ENDPOINT_PATH,
            "get_record",
            SINGLE_DATASET_STORAGE_SIDE_EFFECT,
            "download_file",
            SINGLE_DATASET_DATASET_SIDE_EFFECT,
        ),
        (
            FORMATION_RESISTIVITY_INDEX_SOURCE_ENDPOINT_PATH,
            "get_record",
            NO_DATASETS_STORAGE_SIDE_EFFECT,
            "download_file",
            NO_DATASETS_DATASET_SIDE_EFFECT,
        ),
    ],
)
async def test_get_file_source_success(
    path, storage_method, osdu_records, dataset_method, blobs,
    with_patched_services_success,
):
    with get_overrides():
        async with AsyncClient(base_url=TEST_SERVER, app=app) as client:
            response = await client.get(path, headers=TEST_HEADERS_JSON)

    print(response.content)

    if len(blobs) > 1:
        assert response.status_code == status.HTTP_200_OK
        assert response.headers[CONTENT_TYPE] == SupportedMimeTypes.ZIP.mime_type
    elif len(blobs) == 1:
        assert response.status_code == status.HTTP_200_OK
        assert response.headers[CONTENT_TYPE] == "application/pdf"
        assert b"pdf_content" in response.content
    else:
        assert response.status_code == status.HTTP_404_NOT_FOUND
