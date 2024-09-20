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
import json
import os
from typing import NamedTuple

from app.models.schemas.osdu_storage import Acl, Legal, OsduStorageRecord
from app.resources.paths import CommonRelativePathsV2, PVTModelRelativePaths
from tests.test_api.api_version import API_VERSION_V2

dir_path = os.path.dirname(os.path.abspath(__file__))


class KindVersion:
    V_1_0_0: str = "1.0.0"
    V_1_1_0: str = "1.1.0"
    V_2_0_0: str = "2.0.0"


TEST_SERVER = "http://testserver"
TEST_HEADERS = {
    "content-type": "application/json",
    "data-partition-id": "opendes",
    "Authorization": "Bearer token",
}
TEST_HEADERS_NO_AUTH = {
    "data-partition-id": "opendes",
    "content-type": "application/json",
}
SCHEMA_AUTHORITY = os.getenv("SCHEMA_AUTHORITY", "osdu")
CUSTOM_SCHEMA_AUTHORITY = os.getenv("CUSTOM_SCHEMA_AUTHORITY", "rafsddms")
PARTITION = "partition"
GENERIC_FACILITY_TYPE = "master-data--GenericFacility"
GENERIC_FACILITY_ID = "generic_facility_test"
GENERIC_SITE_TYPE = "master-data--GenericSite"
GENERIC_SITE_ID = "generic_site_test"
SAMPLE_TYPE = "master-data--Sample"
SAMPLE_ID = "sample_test"
SAMPLE_ACQUISITION_JOB_TYPE = "master-data--SampleAcquisitionJob"
SAMPLE_ACQUISITION_JOB_ID = "sample_acquisition_job_test"
SAMPLE_CHAIN_OF_CUSTODY_EVENT_TYPE = "master-data--SampleChainOfCustodyEvent"
SAMPLE_CHAIN_OF_CUSTODY_EVENT_ID = "sample_chain_of_custody_event_test"
SAMPLE_CONTAINER_TYPE = "master-data--SampleContainer"
SAMPLE_CONTAINER_ID = "sample_container_test"
SAMPLESANALYSESREPORT_TYPE = "work-product-component--SamplesAnalysesReport"
SAMPLESANALYSESREPORT_ID = "samplesanalysesreport_test_id"
SAMPLESANALYSIS_TYPE = "work-product-component--SamplesAnalysis"
SAMPLESANALYSIS_ID = "samplesanalysis_test"
FILE_GENERIC_TYPE = "dataset--File.Generic"
TEST_DATASET_UID = "1"

TEST_GENERIC_FACILITY_ID = f"{PARTITION}:{GENERIC_FACILITY_TYPE}:{GENERIC_FACILITY_ID}"
TEST_GENERIC_FACILITY_KIND = f"{SCHEMA_AUTHORITY}:wks:{GENERIC_FACILITY_TYPE}:{KindVersion.V_1_0_0}"
TEST_GENERIC_SITE_ID = f"{PARTITION}:{GENERIC_SITE_TYPE}:{GENERIC_SITE_ID}"
TEST_GENERIC_SITE_KIND = f"{SCHEMA_AUTHORITY}:wks:{GENERIC_SITE_TYPE}:{KindVersion.V_1_0_0}"
TEST_SAMPLE_ID = f"{PARTITION}:{SAMPLE_TYPE}:{SAMPLE_ID}"
TEST_SAMPLE_KIND = f"{SCHEMA_AUTHORITY}:wks:{SAMPLE_TYPE}:{KindVersion.V_2_0_0}"
TEST_SAMPLE_ACQUISITION_JOB_ID = f"{PARTITION}:{SAMPLE_ACQUISITION_JOB_TYPE}:{SAMPLE_ACQUISITION_JOB_ID}"
TEST_SAMPLE_ACQUISITION_JOB_KIND = f"{SCHEMA_AUTHORITY}:wks:{SAMPLE_ACQUISITION_JOB_TYPE}:{KindVersion.V_1_0_0}"
TEST_SAMPLE_CHAIN_OF_CUSTODY_EVENT_ID = f"{PARTITION}:{SAMPLE_CHAIN_OF_CUSTODY_EVENT_TYPE}:{SAMPLE_CHAIN_OF_CUSTODY_EVENT_ID}"
TEST_SAMPLE_CHAIN_OF_CUSTODY_EVENT_KIND = f"{SCHEMA_AUTHORITY}:wks:{SAMPLE_CHAIN_OF_CUSTODY_EVENT_TYPE}:{KindVersion.V_1_0_0}"
TEST_SAMPLE_CONTAINER_ID = f"{PARTITION}:{SAMPLE_CONTAINER_TYPE}:{SAMPLE_CONTAINER_ID}"
TEST_SAMPLE_CONTAINER_KIND = f"{SCHEMA_AUTHORITY}:wks:{SAMPLE_CONTAINER_TYPE}:{KindVersion.V_1_0_0}"
TEST_SAMPLESANALYSESREPORT_ID = f"{PARTITION}:{SAMPLESANALYSESREPORT_TYPE}:{SAMPLESANALYSESREPORT_ID}"
TEST_SAMPLESANALYSESREPORT_KIND_V2 = f"{SCHEMA_AUTHORITY}:wks:{SAMPLESANALYSESREPORT_TYPE}:{KindVersion.V_1_0_0}"
TEST_SAMPLESANALYSIS_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{SAMPLESANALYSIS_ID}"
TEST_SAMPLESANALYSIS_KIND_V2 = f"{SCHEMA_AUTHORITY}:wks:{SAMPLESANALYSIS_TYPE}:{KindVersion.V_1_0_0}"
TEST_ACL = Acl(viewers=["viewers@domain.com"], owners=["owners@domain.com"])
TEST_LEGAL = Legal(legaltags=["legaltag"], otherRelevantDataCountries=["US"], status="compliant")
TEST_WRONG_ID = "partition:entity-type:id"

# PVTModel
TEST_MPFM_CALIBRATION_ID = f"{PARTITION}:work-product-component--MultiPhaseFlowMeterCalibration:{KindVersion.V_1_0_0}"
TEST_PVT_MODEL_ID = f"{PARTITION}:work-product-component--PVTModel:{KindVersion.V_1_0_0}"
TEST_COMPONENT_SCENARIO_ID = f"{PARTITION}:work-product-component--ComponentScenario:{KindVersion.V_1_0_0}"
TEST_BLACK_OIL_TABLE_ID = f"{PARTITION}:work-product-component--BlackOilTable:{KindVersion.V_1_0_0}"

OSDU_GENERIC_RECORD = OsduStorageRecord(
    id="partition:type:identifier",
    kind="partition:wks:type:type_version",
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={"dummy": "data"},
)

GENERIC_FACILITY_RECORD = OsduStorageRecord(
    id=TEST_GENERIC_FACILITY_ID,
    kind=TEST_GENERIC_FACILITY_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={},
)

GENERIC_SITE_RECORD = OsduStorageRecord(
    id=TEST_GENERIC_SITE_ID,
    kind=TEST_GENERIC_SITE_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "Name": "Name",
        "SiteTypeID": "partition:reference-data--SiteType:Coal:",
    },
)

SAMPLE_RECORD = OsduStorageRecord(
    id=TEST_SAMPLE_ID,
    kind=TEST_SAMPLE_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "ResourceHomeRegionID": "partition:reference-data--OSDURegion:Region:",
    },
)

SAMPLE_ACQUISITION_JOB_RECORD = OsduStorageRecord(
    id=TEST_SAMPLE_ACQUISITION_JOB_ID,
    kind=TEST_SAMPLE_ACQUISITION_JOB_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "JobTypeID": "JobTypeID",
        "ReferenceJobNumber": "ReferenceJobNumber",
    },
)

SAMPLE_CHAIN_OF_CUSTODY_EVENT_RECORD = OsduStorageRecord(
    id=TEST_SAMPLE_CHAIN_OF_CUSTODY_EVENT_ID,
    kind=TEST_SAMPLE_CHAIN_OF_CUSTODY_EVENT_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "CustodyEventLocationID": "partition:master-data--Organisation:Organisation:",
        "CustodyEventTypeID": "partition:reference-data--CustodyEventType:SubSampleLive:",
    },
)

SAMPLE_CONTAINER_RECORD = OsduStorageRecord(
    id=TEST_SAMPLE_CONTAINER_ID,
    kind=TEST_SAMPLE_CONTAINER_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "OperatingConditionRating": {
            "Temperature": 1.0,
            "Pressure": 1.0,
        },
        "SampleContainerServiceTypeIDs": ["partition:reference-data--SampleContainerServiceType:NonHydrocarbon:"],
        "ManufacturerID": "partition:master-data--Organisation:Organisation:",
        "SampleContainerTypeID": "partition:reference-data--SampleContainerType:Pressurized.NotPressureCompensated:",
        "ContainerIdentifier": "BTL-12345",
        "Capacity": 100,
    },
)

SAMPLESANALYSESREPORT_RECORD_V2 = OsduStorageRecord(
    id=TEST_SAMPLESANALYSESREPORT_ID,
    kind=TEST_SAMPLESANALYSESREPORT_KIND_V2,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "SampleIDs": [f"{PARTITION}:master-data--Sample:sample_test_id:"],
        "ReportSampleIdentifiers": ["45H", "49H"],
        "SampleAnalysisTypeIDs": [
            "partition:reference-data--SampleAnalysisType:CapillaryPressureGasOil:",
            "partition:reference-data--SampleAnalysisType:CentrifugeDrainageGasOil:",
        ],
        "SamplesAnalysisCategoryTagIDs": [
            "partition:reference-data--SamplesAnalysisCategoryTag:SCAL:",
        ],
    },
)


SAMPLESANALYSIS_RECORD_V2 = OsduStorageRecord(
    id=TEST_SAMPLESANALYSIS_ID,
    kind=TEST_SAMPLESANALYSIS_KIND_V2,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={
        "ParentSamplesAnalysesReports": [
            {
                "ParentSamplesAnalysesReportID": f"{TEST_SAMPLESANALYSESREPORT_ID}:",
            },
        ],
        "SampleAnalysisTypeIDs": [
            "partition:reference-data--SampleAnalysisType:CapillaryPressureGasOil:",
            "partition:reference-data--SampleAnalysisType:CentrifugeDrainageGasOil:",
        ],
        "Parameters": [],
    },
)

SAMPLESANALYSIS_RECORD_WITHOUT_PARENT_V2 = copy.deepcopy(SAMPLESANALYSIS_RECORD_V2)


def build_storage_service_response_200(
    record_count: int = 1,
    record_ids: list = None,
    skipped_record_ids: list = None,
    record_id_versions: list = None,
):
    return {
        "recordCount": record_count,
        "recordIds": record_ids or ["partition:type:test"],
        "skippedRecordIds": skipped_record_ids or [],
        "recordIdVersions": record_id_versions or ["partition:type:test:1"],
    }


STORAGE_SERVICE_200_RESPONSE = {
    "recordCount": 1,
    "recordIds": ["partition:type:test"],
    "skippedRecordIds": [],
    "recordIdVersions": ["partition:type:test:1"],
}

EXPECTED_404_RESPONSE = {"code": 404, "reason": str(b"test reason"), "message": "test txt"}
EXPECTED_422_NO_KIND_RESPONSE = {"code": 422, "reason": "Unprocessable entity.", "errors": ["kind field required"]}
EXPECTED_422_INVALID_KIND_REASON = "Kind `{}` not supported in RAFS-DDMS."
EXPECTED_422_WRONG_PATTERN = ["ValidationError", "string does not match regex"]
EXPECTED_422_TYPER_ERROR_LIST = "body value is not a valid list"
EXPECTED_200_CREATED_RESPONSE = {
    "recordCount": 1,
    "recordIdVersions": ["partition:type:test:1"],
    "skippedRecordCount": 0,
}

STORAGE_SERVICE_200_VERSIONS_RESPONSE = {
    "recordId": "partition:type:test",
    "versions": [1, 2],
}
EXPECTED_200_VERSIONS_RESPONSE = STORAGE_SERVICE_200_VERSIONS_RESPONSE

# V2 endpoint paths
SAMPLESANALYSES_REPORT_ENDPOINT_PATH_V2 = f"/api/os-rafs-ddms/{API_VERSION_V2}/samplesanalysesreport"
SAMPLESANALYSIS_ENDPOINT_PATH_V2 = f"/api/os-rafs-ddms/{API_VERSION_V2}/samplesanalysis"
MASTER_DATA_ENDPOINT_PATH_V2 = f"/api/os-rafs-ddms/{API_VERSION_V2}/masterdata"

# data endpoints v2
BASE_V2_PATH = f"api/os-rafs-ddms/{API_VERSION_V2}"

SAMPLESANALYSIS_ENDPOINT_PATH = f"{BASE_V2_PATH}/samplesanalysis"
BASE_DATA_V2_PATH = f"{SAMPLESANALYSIS_ENDPOINT_PATH}/{TEST_SAMPLESANALYSIS_ID}"

common_relative_paths_v2 = CommonRelativePathsV2()


class TestContentPathsApiV2:
    RCA = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.ROUTINECOREANALYSIS}"
    CCE = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CCE}"
    DIFF_LIB = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.DIFF_LIB}"
    TRANSPORT_TEST = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.TRANSPORT_TEST}"
    COMPOSITIONAL_ANALYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.COMPOSITIONAL_ANALYSIS}"
    MSS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.MSS}"
    SWELLING = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.SWELLING}"
    CVD = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CVD}"
    WATER_ANALYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.WATER_ANALYSIS}"
    INTERFACIAL_TENSION = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.INTERFACIAL_TENSION}"
    VLE = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.VLE}"
    MCM = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.MCM}"
    SLIMTUBE = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.SLIMTUBE}"
    EXTRACTION = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.EXTRACTION}"
    FRACTIONATION = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.FRACTIONATION}"
    RELATIVE_PERMEABILITY = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.RELATIVE_PERMEABILITY}"
    ROCK_COMPRESSIBILITY = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.ROCK_COMPRESSIBILITY}"
    NMR = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.NMR}"
    MULTIPLE_SALINITY = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.MULTIPLE_SALINITY}"
    GCMS_ALKANES = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GCMS_ALKANES}"
    GCMS_AROMATICS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GCMS_AROMATICS}"
    GCMS_RATIOS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GCMS_RATIOS}"
    GAS_CHROMATOGRAPHY = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GAS_CHROMATOGRAPHY}"
    GAS_COMPOSITION = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GAS_COMPOSITION}"
    ISOTOPE_ANALYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.ISOTOPE_ANALYSIS}"
    BULK_PYROLYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.BULK_PYROLYSIS}"
    CORE_GAMMA = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CORE_GAMMA}"
    MINING_GEOTECH_LOGGING = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.MINING_GEOTECH_LOGGING}"
    UNIAXIAL_TEST = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.UNIAXIAL_TEST}"
    GCMSMS_ANALYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.GCMSMS_ANALYSIS}"
    CEC_CONTENT = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CEC_CONTENT}"
    ELECTRICAL_PROPERTIES = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.ELECTRICAL_PROPERTIES}"
    TRIAXIAL_TEST = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.TRIAXIAL_TEST}"
    CAP_PRESSURE = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CAP_PRESSURE}"
    WETTABILITY_INDEX = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.WETTABILITY_INDEX}"
    TEC = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.TEC}"
    EDS_MAPPING = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.EDS_MAPPING}"
    XRF = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.XRF}"
    TENSILE_STRENGTH = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.TENSILE_STRENGTH}"
    VITRINITE_REFLECTANCE = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.VITRINITE_REFLECTANCE}"
    XRD = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.XRD}"
    PDP = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.PDP}"
    STO = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.STO}"
    CRUSHED_ROCK_ANALYSIS = f"{BASE_DATA_V2_PATH}{common_relative_paths_v2.CRUSHED_ROCK_ANALYSIS}"


class BulkDatasetIdV2(NamedTuple):
    RCA = f"{PARTITION}:{FILE_GENERIC_TYPE}:routinecoreanalysis-{TEST_DATASET_UID}"
    CCE = f"{PARTITION}:{FILE_GENERIC_TYPE}:constantcompositionexpansion-{TEST_DATASET_UID}"
    DIFF_LIB = f"{PARTITION}:{FILE_GENERIC_TYPE}:differentialliberation-{TEST_DATASET_UID}"
    TRANSPORT_TEST = f"{PARTITION}:{FILE_GENERIC_TYPE}:transport-{TEST_DATASET_UID}"
    COMPOSITIONAL_ANALYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:compositionalanalysis-{TEST_DATASET_UID}"
    MSS = f"{PARTITION}:{FILE_GENERIC_TYPE}:multistageseparator-{TEST_DATASET_UID}"
    SWELLING = f"{PARTITION}:{FILE_GENERIC_TYPE}:swelling-{TEST_DATASET_UID}"
    CVD = f"{PARTITION}:{FILE_GENERIC_TYPE}:constantvolumedepletion-{TEST_DATASET_UID}"
    WATER_ANALYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:wateranalysis-{TEST_DATASET_UID}"
    INTERFACIAL_TENSION = f"{PARTITION}:{FILE_GENERIC_TYPE}:interfacialtension-{TEST_DATASET_UID}"
    VLE = f"{PARTITION}:{FILE_GENERIC_TYPE}:vaporliquidequilibrium-{TEST_DATASET_UID}"
    MCM = f"{PARTITION}:{FILE_GENERIC_TYPE}:multiplecontactmiscibility-{TEST_DATASET_UID}"
    SLIMTUBE = f"{PARTITION}:{FILE_GENERIC_TYPE}:slimtube-{TEST_DATASET_UID}"
    EXTRACTION = f"{PARTITION}:{FILE_GENERIC_TYPE}:extraction-{TEST_DATASET_UID}"
    FRACTIONATION = f"{PARTITION}:{FILE_GENERIC_TYPE}:fractionation-{TEST_DATASET_UID}"
    RELATIVE_PERMEABILITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:relativepermeability-{TEST_DATASET_UID}"
    ROCK_COMPRESSIBILITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:rockcompressibility-{TEST_DATASET_UID}"
    ELECTRICAL_PROPERTIES = f"{PARTITION}:{FILE_GENERIC_TYPE}:electricalproperties-{TEST_DATASET_UID}"
    NMR = f"{PARTITION}:{FILE_GENERIC_TYPE}:nmr-{TEST_DATASET_UID}"
    MULTIPLE_SALINITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:multiplesalinitytests-{TEST_DATASET_UID}"
    GCMS_ALKANES = f"{PARTITION}:{FILE_GENERIC_TYPE}:gcmsalkanes-{TEST_DATASET_UID}"
    GCMS_AROMATICS = f"{PARTITION}:{FILE_GENERIC_TYPE}:gcmsaromatics-{TEST_DATASET_UID}"
    GCMS_RATIOS = f"{PARTITION}:{FILE_GENERIC_TYPE}:gcmsratios-{TEST_DATASET_UID}"
    GAS_CHROMATOGRAPHY = f"{PARTITION}:{FILE_GENERIC_TYPE}:gaschromatographyanalyses-{TEST_DATASET_UID}"
    GAS_COMPOSITION = f"{PARTITION}:{FILE_GENERIC_TYPE}:gascompositionanalyses-{TEST_DATASET_UID}"
    ISOTOPE_ANALYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:isotopes-{TEST_DATASET_UID}"
    BULK_PYROLYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:bulkpyrolysisanalyses-{TEST_DATASET_UID}"
    CORE_GAMMA = f"{PARTITION}:{FILE_GENERIC_TYPE}:coregamma-{TEST_DATASET_UID}"
    MINING_GEOTECH_LOGGING = f"{PARTITION}:{FILE_GENERIC_TYPE}:mininggeotechlogging-{TEST_DATASET_UID}"
    UNIAXIAL_TEST = f"{PARTITION}:{FILE_GENERIC_TYPE}:uniaxial-{TEST_DATASET_UID}"
    GCMSMS_ANALYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:gcmsms-{TEST_DATASET_UID}"
    CEC_CONTENT = f"{PARTITION}:{FILE_GENERIC_TYPE}:cec-{TEST_DATASET_UID}"
    TRIAXIAL_TEST = f"{PARTITION}:{FILE_GENERIC_TYPE}:triaxial-{TEST_DATASET_UID}"
    CAP_PRESSURE = f"{PARTITION}:{FILE_GENERIC_TYPE}:capillarypressure-{TEST_DATASET_UID}"
    WETTABILITY_INDEX = f"{PARTITION}:{FILE_GENERIC_TYPE}:wettabilityindex-{TEST_DATASET_UID}"
    TEC = f"{PARTITION}:{FILE_GENERIC_TYPE}:tec-{TEST_DATASET_UID}"
    EDS_MAPPING = f"{PARTITION}:{FILE_GENERIC_TYPE}:edsmapping-{TEST_DATASET_UID}"
    XRF = f"{PARTITION}:{FILE_GENERIC_TYPE}:xrf-{TEST_DATASET_UID}"
    TENSILE_STRENGTH = f"{PARTITION}:{FILE_GENERIC_TYPE}:tensilestrength-{TEST_DATASET_UID}"
    VITRINITE_REFLECTANCE = f"{PARTITION}:{FILE_GENERIC_TYPE}:vitrinitereflectance-{TEST_DATASET_UID}"
    XRD = f"{PARTITION}:{FILE_GENERIC_TYPE}:xrd-{TEST_DATASET_UID}"
    PDP = f"{PARTITION}:{FILE_GENERIC_TYPE}:pdp-{TEST_DATASET_UID}"
    STO = f"{PARTITION}:{FILE_GENERIC_TYPE}:stocktankoilanalysisreports-{TEST_DATASET_UID}"
    CRUSHED_ROCK_ANALYSIS = f"{PARTITION}:{FILE_GENERIC_TYPE}:crushedrockanalysis-{TEST_DATASET_UID}"


with open(f"{dir_path}/schemas/wpc_definitions.json") as fp:
    WPC_DEFINITIONS = json.load(fp)

with open(f"{dir_path}/schemas/samples_analyses_report.json") as fp:
    SAMPLES_ANALYSES_REPORT_SCHEMA = json.load(fp)
    SAMPLES_ANALYSES_REPORT_SCHEMA["definitions"] = WPC_DEFINITIONS

with open(f"{dir_path}/schemas/samples_analysis.json") as fp:
    SAMPLES_ANALYSIS_SCHEMA = json.load(fp)
    SAMPLES_ANALYSIS_SCHEMA["definitions"] = WPC_DEFINITIONS

with open(f"{dir_path}/schemas/md_definitions.json") as fp:
    MD_DEFINITIONS = json.load(fp)

with open(f"{dir_path}/schemas/sample.json") as fp:
    SAMPLE_SCHEMA = json.load(fp)
    SAMPLE_SCHEMA["definitions"] = MD_DEFINITIONS

with open(f"{dir_path}/schemas/sample_acquisition_job.json") as fp:
    SAMPLE_ACQUISITION_JOB_SCHEMA = json.load(fp)
    SAMPLE_ACQUISITION_JOB_SCHEMA["definitions"] = MD_DEFINITIONS

with open(f"{dir_path}/schemas/sample_chain_of_custody_event.json") as fp:
    SAMPLE_CHAIN_OF_CUSTODY_EVENT_SCHEMA = json.load(fp)
    SAMPLE_CHAIN_OF_CUSTODY_EVENT_SCHEMA["definitions"] = MD_DEFINITIONS

with open(f"{dir_path}/schemas/sample_container.json") as fp:
    SAMPLE_CONTAINER_SCHEMA = json.load(fp)
    SAMPLE_CONTAINER_SCHEMA["definitions"] = MD_DEFINITIONS

# PVT Model
PVT_MODEL_ENDPOINT_PATH = f"{BASE_V2_PATH}/pvtmodel"
BASE_MPFM_CALIBRATION_CONTENT_PATH = f"{PVT_MODEL_ENDPOINT_PATH}/{TEST_MPFM_CALIBRATION_ID}"
BASE_PVT_MODEL_CONTENT_PATH = f"{PVT_MODEL_ENDPOINT_PATH}/{TEST_PVT_MODEL_ID}"
BASE_COMPONENT_SCENARIO_CONTENT_PATH = f"{PVT_MODEL_ENDPOINT_PATH}/{TEST_COMPONENT_SCENARIO_ID}"
BASE_BLACK_OIL_TABLE_CONTENT_PATH = f"{PVT_MODEL_ENDPOINT_PATH}/{TEST_BLACK_OIL_TABLE_ID}"

pvt_model_relative_paths = PVTModelRelativePaths()


class TestContentPathsPVTModel:
    MPFM_CALIBRATION = f"{BASE_MPFM_CALIBRATION_CONTENT_PATH}{pvt_model_relative_paths.MPFM_CALIBRATION}"
    EOS = f"{BASE_PVT_MODEL_CONTENT_PATH}{pvt_model_relative_paths.EOS}"
    COMPONENT_SCENARIO = f"{BASE_COMPONENT_SCENARIO_CONTENT_PATH}{pvt_model_relative_paths.COMPONENT_SCENARIO}"
    BLACK_OIL_TABLE = f"{BASE_BLACK_OIL_TABLE_CONTENT_PATH}{pvt_model_relative_paths.BLACK_OIL_TABLE}"


class BulkDatasetIdPVTModel(NamedTuple):
    MPFM_CALIBRATION = f"{PARTITION}:{FILE_GENERIC_TYPE}:mpfmcalibrationdata-{TEST_DATASET_UID}"
    EOS = f"{PARTITION}:{FILE_GENERIC_TYPE}:equationofstatedata-{TEST_DATASET_UID}"
    COMPONENT_SCENARIO = f"{PARTITION}:{FILE_GENERIC_TYPE}:componentscenariodata-{TEST_DATASET_UID}"
    BLACK_OIL_TABLE = f"{PARTITION}:{FILE_GENERIC_TYPE}:blackoiltabledata-{TEST_DATASET_UID}"
