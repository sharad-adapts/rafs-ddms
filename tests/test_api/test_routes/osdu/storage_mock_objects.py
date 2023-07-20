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
import os
from typing import NamedTuple

from app.models.domain.osdu.MDCoring100 import Coring
from app.models.domain.osdu.MDCoring100 import Data as CoringData
from app.models.domain.osdu.MDRockSample100 import Data as RockSampleData
from app.models.domain.osdu.MDRockSample100 import RockSample
from app.models.domain.osdu.WPCCCE100 import ConstantCompositionExpansionTest
from app.models.domain.osdu.WPCCCE100 import Data as CceData
from app.models.domain.osdu.WPCCompositionalAnalysis100 import (
    CompositionalAnalysis,
)
from app.models.domain.osdu.WPCCompositionalAnalysis100 import (
    Data as CompositionalAnalysisData,
)
from app.models.domain.osdu.WPCConstantVolumeDepletionTest100 import (
    ConstantVolumeDepletionTest,
)
from app.models.domain.osdu.WPCConstantVolumeDepletionTest100 import (
    Data as CVDData,
)
from app.models.domain.osdu.WPCDifLib100 import Data as DifLibData
from app.models.domain.osdu.WPCDifLib100 import DifferentialLiberationTest
from app.models.domain.osdu.WPCInterfacialTension100 import (
    Data as InterfacialTensionData,
)
from app.models.domain.osdu.WPCInterfacialTension100 import (
    InterfacialTensionTest,
)
from app.models.domain.osdu.WPCMCM100 import Data as MCMData
from app.models.domain.osdu.WPCMCM100 import MultipleContactMiscibilityTest
from app.models.domain.osdu.WPCMSS100 import Data as MSSData
from app.models.domain.osdu.WPCMSS100 import MultiStageSeparatorTest
from app.models.domain.osdu.WPCPVT100 import PVT
from app.models.domain.osdu.WPCPVT100 import Data as PVTData
from app.models.domain.osdu.WPCPVT100 import PVTTests
from app.models.domain.osdu.WPCRockSampleAnalysis110 import (
    Data as RockSampleAnalysisData,
)
from app.models.domain.osdu.WPCRockSampleAnalysis110 import RockSampleAnalysis
from app.models.domain.osdu.WPCSamplesAnalysesReport100 import (
    Data as SamplesAnalysesReportData,
)
from app.models.domain.osdu.WPCSamplesAnalysesReport100 import (
    SamplesAnalysesReport,
)
from app.models.domain.osdu.WPCSamplesAnalysis100 import (
    Data as SamplesAnalysisData,
)
from app.models.domain.osdu.WPCSamplesAnalysis100 import SamplesAnalysis
from app.models.domain.osdu.WPCSlimTubeTest100 import Data as SlimTubeTestData
from app.models.domain.osdu.WPCSlimTubeTest100 import SlimTubeTest
from app.models.domain.osdu.WPCSTO100 import Data as STOData
from app.models.domain.osdu.WPCSTO100 import StockTankOilAnalysisTest
from app.models.domain.osdu.WPCSwellingTest100 import Data as SwellingData
from app.models.domain.osdu.WPCSwellingTest100 import SwellingTest
from app.models.domain.osdu.WPCTransportTest100 import Data as TransportTestData
from app.models.domain.osdu.WPCTransportTest100 import TransportTest
from app.models.domain.osdu.WPCVLE100 import Data as VLEData
from app.models.domain.osdu.WPCVLE100 import VaporLiquidEquilibriumTest
from app.models.domain.osdu.WPCWaterAnalysis100 import Data as WaterAnalysisData
from app.models.domain.osdu.WPCWaterAnalysis100 import WaterAnalysisTest
from app.models.schemas.osdu_storage import Acl, Legal, OsduStorageRecord
from tests.test_api.api_version import API_VERSION

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
CORING_TYPE = "master-data--Coring"
CORING_VERSION = "1.0.0"
CORING_ID = "coring_test"
ROCKSAMPLE_TYPE = "master-data--RockSample"
ROCKSAMPLE_VERSION = "1.0.0"
ROCKSAMPLE_ID = "rocksample_test"
ROCKSAMPLEANALYSIS_TYPE = "work-product-component--RockSampleAnalysis"
ROCKSAMPLEANALYSIS_VERSION = "1.1.0"
ROCKSAMPLEANALYSIS_ID = "rocksampleanalysis_test"
CCE_TYPE = "work-product-component--ConstantCompositionExpansionTest"
CCE_VERSION = "1.0.0"
CCE_ID = "cce-test"
PVT_TYPE = "work-product-component--PVT"
PVT_ID = "pvt_test"
PVT_VERSION = "1.0.0"
WELL_TYPE = "master-data--Well"
WELL_ID = "well_test"
WELLBORE_TYPE = "master-data--Wellbore"
WELLBORE_ID = "wellbore_test"
DL_TYPE = "work-product-component--DifferentialLiberationTest"
DL_VERSION = "1.0.0"
DL_ID = "dlt_test"
TRANSPORT_TYPE = "work-product-component--TransportTest"
TRANSPORT_VERSION = "1.0.0"
TRANSPORT_ID = "transport_test"
COMPOSITIONALANALYSIS_TYPE = "work-product-component--CompositionalAnalysisTest"
COMPOSITIONALANALYSIS_ID = "compositionalanalysis_test"
COMPOSITIONALANALYSIS_VERSION = "1.0.0"
FLUIDSAMPLE_TYPE = "master-data--FluidSample"
FLUIDSAMPLE_ID = "fluidsample_test"
MSS_TYPE = "work-product-component--MultiStageSeparatorTest"
MSS_ID = "multistageseparator_test"
MSS_VERSION = "1.0.0"
SWELLING_TYPE = "work-product-component--SwellingTest"
SWELLING_ID = "swelling_test"
SWELLING_VERSION = "1.0.0"
CVD_TYPE = "work-product-component--ConstantVolumeDepletionTest"
CVD_VERSION = "1.0.0"
CVD_ID = "cvd_test"
WATER_ANALYSIS_TYPE = "work-product-component--WaterAnalysisTest"
WATER_ANALYSIS_VERSION = "1.0.0"
WATER_ANALYSIS_ID = "wateranalysis_test"
STO_TYPE = "work-product-component--StockTankOilAnalysisTest"
STO_VERSION = "1.0.0"
STO_ID = "sto_test"
INTERFACIAL_TENSION_TYPE = "work-product-component--InterfacialTensionTest"
INTERFACIAL_TENSION_VERSION = "1.0.0"
INTERFACIAL_TENSION_ID = "intefacialtension_test"
VLE_TYPE = "work-product-component--VaporLiquidEquilibriumTest"
VLE_VERSION = "1.0.0"
VLE_ID = "vle_test"
MCM_TYPE = "work-product-component--MultipleContactMiscibilityTest"
MCM_VERSION = "1.0.0"
MCM_ID = "mcm_test"
SLIMTUBETEST_TYPE = "work-product-component--SlimTubeTest"
SLIMTUBETEST_VERSION = "1.0.0"
SLIMTUBETEST_ID = "slimtubetest_test"
SAMPLESANALYSESREPORT_TYPE = "work-product-component--SamplesAnalysesReport"
SAMPLESANALYSESREPORT_VERSION = "1.0.0"
SAMPLESANALYSESREPORT_ID = "samplesanalysesreport_test_id"
SAMPLESANALYSIS_TYPE = "work-product-component--SamplesAnalysis"
SAMPLESANALYSIS_VERSION = "1.0.0"
SAMPLESANALYSIS_ID = "samplesanalysis_test"
RELATIVE_PERMEABILITY_ID = "relative_permeability_test"
CAP_PRESSURE_ID = "cappressure_test"
FRACTIONATION_ID = "fractionation_test"
EXTRACTION_ID = "extraction_test"
PHYS_CHEM_ID = "physchem_test"
WATER_GAS_RELATIVE_PERMEABILITY_ID = "watergasrelativepermeability_test"
ROCK_COMPRESSIBILITY_ID = "rock_compressibility_test"
ELECTRICAL_PROPERTIES_ID = "electricalproperties_test"
FORMATION_RESISTIVITY_INDEX_ID = "formationresistivityindexes_test"
FILE_GENERIC_TYPE = "dataset--File.Generic"
TEST_DATASET_UID = "1"

TEST_CORING_ID = f"{PARTITION}:{CORING_TYPE}:{CORING_ID}"
TEST_CORING_KIND = f"{SCHEMA_AUTHORITY}:wks:{CORING_TYPE}:{CORING_VERSION}"
TEST_ROCKSAMPLE_ID = f"{PARTITION}:{ROCKSAMPLE_TYPE}:{ROCKSAMPLE_ID}"
TEST_ROCKSAMPLE_KIND = f"{SCHEMA_AUTHORITY}:wks:{ROCKSAMPLE_TYPE}:{ROCKSAMPLE_VERSION}"
TEST_ROCKSAMPLEANALYSIS_ID = f"{PARTITION}:{ROCKSAMPLEANALYSIS_TYPE}:{ROCKSAMPLEANALYSIS_ID}"
TEST_ROCKSAMPLEANALYSIS_KIND = f"{SCHEMA_AUTHORITY}:wks:{ROCKSAMPLEANALYSIS_TYPE}:{ROCKSAMPLEANALYSIS_VERSION}"
TEST_CCE_ID = f"{PARTITION}:{CCE_TYPE}:{CCE_ID}"
TEST_CCE_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{CCE_TYPE}:{CCE_VERSION}"
TEST_PVT_ID = f"{PARTITION}:{PVT_TYPE}:{PVT_ID}"
TEST_PVT_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{PVT_TYPE}:{PVT_VERSION}"
TEST_WELLBORE_ID = f"{PARTITION}:{WELLBORE_TYPE}:{WELLBORE_ID}"
TEST_DL_ID = f"{PARTITION}:{DL_TYPE}:{DL_ID}"
TEST_DL_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{DL_TYPE}:{DL_VERSION}"
TEST_TRANSPORT_ID = f"{PARTITION}:{TRANSPORT_TYPE}:{TRANSPORT_ID}"
TEST_TRANSPORT_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{TRANSPORT_TYPE}:{TRANSPORT_VERSION}"
TEST_COMPOSITIONALANALYSIS_ID = f"{PARTITION}:{COMPOSITIONALANALYSIS_TYPE}:{COMPOSITIONALANALYSIS_ID}"
TEST_COMPOSITIONALANALYSIS_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{COMPOSITIONALANALYSIS_TYPE}:{COMPOSITIONALANALYSIS_VERSION}"
TEST_MSS_ID = f"{PARTITION}:{MSS_TYPE}:{MSS_ID}"
TEST_MSS_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{MSS_TYPE}:{MSS_VERSION}"
TEST_SWELLING_ID = f"{PARTITION}:{SWELLING_TYPE}:{SWELLING_ID}"
TEST_SWELLING_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{SWELLING_TYPE}:{SWELLING_VERSION}"
TEST_CVD_ID = f"{PARTITION}:{CVD_TYPE}:{CVD_ID}"
TEST_CVD_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{CVD_TYPE}:{CVD_VERSION}"
TEST_WATERANALYSIS_ID = f"{PARTITION}:{WATER_ANALYSIS_TYPE}:{WATER_ANALYSIS_ID}"
TEST_WATERANALYSIS_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{WATER_ANALYSIS_TYPE}:{WATER_ANALYSIS_VERSION}"
TEST_STO_ID = f"{PARTITION}:{STO_TYPE}:{STO_ID}"
TEST_STO_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{STO_TYPE}:{STO_VERSION}"
TEST_INTERFACIAL_TENSION_ID = f"{PARTITION}:{INTERFACIAL_TENSION_TYPE}:{INTERFACIAL_TENSION_ID}"
TEST_INTERFACIAL_TENSION_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{INTERFACIAL_TENSION_TYPE}:{INTERFACIAL_TENSION_VERSION}"
TEST_VLE_ID = f"{PARTITION}:{VLE_TYPE}:{VLE_ID}"
TEST_VLE_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{VLE_TYPE}:{VLE_VERSION}"
TEST_MCM_ID = f"{PARTITION}:{MCM_TYPE}:{MCM_ID}"
TEST_MCM_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{MCM_TYPE}:{MCM_VERSION}"
TEST_SLIMTUBETEST_ID = f"{PARTITION}:{SLIMTUBETEST_TYPE}:{SLIMTUBETEST_ID}"
TEST_SLIMTUBETEST_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{SLIMTUBETEST_TYPE}:{SLIMTUBETEST_VERSION}"
TEST_SAMPLESANALYSESREPORT_ID = f"{PARTITION}:{SAMPLESANALYSESREPORT_TYPE}:{SAMPLESANALYSESREPORT_ID}"
TEST_SAMPLESANALYSESREPORT_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{SAMPLESANALYSESREPORT_TYPE}:{SAMPLESANALYSESREPORT_VERSION}"
TEST_SAMPLESANALYSIS_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{SAMPLESANALYSIS_ID}"
TEST_SAMPLESANALYSIS_KIND = f"{CUSTOM_SCHEMA_AUTHORITY}:wks:{SAMPLESANALYSIS_TYPE}:{SAMPLESANALYSIS_VERSION}"
TEST_CAP_PRESSURE_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{CAP_PRESSURE_ID}"
TEST_FLUIDSAMPLE_ID = f"{PARTITION}:{FLUIDSAMPLE_TYPE}:{FLUIDSAMPLE_ID}"
TEST_RELATIVE_PERMEABILITY_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{RELATIVE_PERMEABILITY_ID}"
TEST_FRACTIONATION_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{FRACTIONATION_ID}"
TEST_EXTRACTION_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{EXTRACTION_ID}"
TEST_PHYS_CHEM_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{PHYS_CHEM_ID}"
TEST_WATER_GAS_RELATIVE_PERMEABILITY_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{WATER_GAS_RELATIVE_PERMEABILITY_ID}"
TEST_ROCK_COMPRESSIBILITY_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{ROCK_COMPRESSIBILITY_ID}"
TEST_ELECTRICAL_PROPERTIES_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{ELECTRICAL_PROPERTIES_ID}"
TEST_FORMATION_RESISTIVITY_INDEX_ID = f"{PARTITION}:{SAMPLESANALYSIS_TYPE}:{FORMATION_RESISTIVITY_INDEX_ID}"
TEST_ACL = Acl(viewers=["viewers@domain.com"], owners=["owners@domain.com"])
TEST_LEGAL = Legal(legaltags=["legaltag"], otherRelevantDataCountries=["US"], status="compliant")
TEST_WRONG_ID = "partition:entity-type:id"

OSDU_GENERIC_RECORD = OsduStorageRecord(
    id="partition:type:identifier",
    kind="partition:wks:type:type_version",
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data={"dummy": "data"},
)

CORING_RECORD = Coring(
    id=TEST_CORING_ID,
    kind=TEST_CORING_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=CoringData(CoreNumber="CoreNumber", WellboreID=f"{TEST_WELLBORE_ID}:"),
)

ROCKSAMPLE_RECORD = RockSample(
    id=TEST_ROCKSAMPLE_ID,
    kind=TEST_ROCKSAMPLE_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=RockSampleData(
        CoringID=f"{TEST_CORING_ID}:",
        WellboreID=f"{TEST_WELLBORE_ID}:",
    ),
)

ROCKSAMPLEANALYSIS_RECORD = RockSampleAnalysis(
    id=TEST_ROCKSAMPLEANALYSIS_ID,
    kind=TEST_ROCKSAMPLEANALYSIS_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=RockSampleAnalysisData(
        CoringID=f"{TEST_CORING_ID}:",
        WellboreID=f"{TEST_WELLBORE_ID}:",
    ),
)

PVT_RECORD = PVT(
    id=TEST_PVT_ID,
    kind=TEST_PVT_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=PVTData(
        PVTTests=PVTTests(
            ConstantCompositionExpansionTestID=[f"{TEST_CCE_ID}:"],
            DifferentialLiberationTestID=[f"{TEST_DL_ID}:"],
        ),
    ),
)

CCE_RECORD = ConstantCompositionExpansionTest(
    id=TEST_CCE_ID,
    kind=TEST_CCE_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=CceData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

DL_RECORD = DifferentialLiberationTest(
    id=TEST_DL_ID,
    kind=TEST_DL_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=DifLibData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

TRANSPORT_RECORD = TransportTest(
    id=TEST_TRANSPORT_ID,
    kind=TEST_TRANSPORT_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=TransportTestData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

COMPOSITIONALANALYSIS_RECORD = CompositionalAnalysis(
    id=TEST_COMPOSITIONALANALYSIS_ID,
    kind=TEST_COMPOSITIONALANALYSIS_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=CompositionalAnalysisData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

MULTISTAGESEPARATOR_RECORD = MultiStageSeparatorTest(
    id=TEST_MSS_ID,
    kind=TEST_MSS_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=MSSData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

SWELLING_RECORD = SwellingTest(
    id=TEST_SWELLING_ID,
    kind=TEST_SWELLING_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=SwellingData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

CVD_RECORD = ConstantVolumeDepletionTest(
    id=TEST_CVD_ID,
    kind=TEST_CVD_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=CVDData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

WATERANALYSIS_RECORD = WaterAnalysisTest(
    id=TEST_WATERANALYSIS_ID,
    kind=TEST_WATERANALYSIS_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=WaterAnalysisData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

STO_RECORD = StockTankOilAnalysisTest(
    id=TEST_STO_ID,
    kind=TEST_STO_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=STOData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

INTERFACIAL_TENSION_RECORD = InterfacialTensionTest(
    id=TEST_INTERFACIAL_TENSION_ID,
    kind=TEST_INTERFACIAL_TENSION_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=InterfacialTensionData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

VLE_RECORD = VaporLiquidEquilibriumTest(
    id=TEST_VLE_ID,
    kind=TEST_VLE_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=VLEData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

MCM_RECORD = MultipleContactMiscibilityTest(
    id=TEST_MCM_ID,
    kind=TEST_MCM_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=MCMData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

SLIMTUBETEST_RECORD = SlimTubeTest(
    id=TEST_SLIMTUBETEST_ID,
    kind=TEST_SLIMTUBETEST_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=SlimTubeTestData(
        PVTReportID=f"{TEST_PVT_ID}:",
        FluidSampleID=f"{TEST_FLUIDSAMPLE_ID}:",
        LabSampleIdentifier="20207905-20",
        LaboratoryName="CoreLab",
    ),
)

SAMPLESANALYSESREPORT_RECORD = SamplesAnalysesReport(
    id=TEST_SAMPLESANALYSESREPORT_ID,
    kind=TEST_SAMPLESANALYSESREPORT_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=SamplesAnalysesReportData(
        SampleIDs=[f"{PARTITION}:master-data--Sample:sample_test_id:"],
        ReportSampleIdentifiers=["45H", "49H"],
        SampleAnalysisTypeIDs=["CapillaryPressureGasOil", "CentrifugeDrainageGasOil"],
        SamplesAnalysisCategoryTagIDs=["SCAL"],
    ),
)

SAMPLESANALYSIS_RECORD = SamplesAnalysis(
    id=TEST_SAMPLESANALYSIS_ID,
    kind=TEST_SAMPLESANALYSIS_KIND,
    acl=TEST_ACL,
    legal=TEST_LEGAL,
    data=SamplesAnalysisData(
        ParentSamplesAnalysesReports=[f"{TEST_SAMPLESANALYSESREPORT_ID}:"],
    ),
)

SAMPLESANALYSIS_RECORD_WITHOUT_PARENT = copy.deepcopy(SAMPLESANALYSIS_RECORD)
SAMPLESANALYSIS_RECORD_WITHOUT_PARENT.data.ParentSamplesAnalysesReports = []


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
PVT_STORAGE_SERVICE_200_RESPONSE = {
    "recordCount": 1,
    "recordIds": [TEST_PVT_ID],
    "skippedRecordIds": [],
    "recordIdVersions": [f"{TEST_PVT_ID}:1"],
}
PVT_QUERY_STORAGE_SERVICE_200_RESPONSE = {
    "records": [
        PVT_RECORD.dict(exclude_none=True),
    ],
    "invalidRecords": [],
    "retryRecords": [],
}
PVT_QUERY_STORAGE_SERVICE_INVALID_PVT_200_RESPONSE = {
    "records": [
        PVT_RECORD.dict(exclude_none=True),
    ],
    "invalidRecords": [],
    "retryRecords": [],
}

EXPECTED_404_RESPONSE = {"code": 404, "reason": str(b"test reason"), "message": "test txt"}
EXPECTED_422_NO_KIND_REASON = "'loc': ('kind',), 'msg': 'string does not match regex"
EXPECTED_422_WRONG_PATTERN = ["ValidationError", "string does not match regex"]
EXPECTED_422_TYPER_ERROR_LIST = "body value is not a valid list"
EXPECTED_200_CREATED_RESPONSE = {
    "recordCount": 1,
    "recordIdVersions": ["partition:type:test:1"],
    "skippedRecordCount": 0,
}
EXPECTED_200_CREATED_PVT_UPDATED_RESPONSE = {
    "recordCount": 2,
    "recordIdVersions": ["partition:type:test:1", "partition:pvt_type:test:1"],
    "skippedRecordCount": 0,
}

STORAGE_SERVICE_200_VERSIONS_RESPONSE = {
    "recordId": "partition:type:test",
    "versions": [1, 2],
}
EXPECTED_200_VERSIONS_RESPONSE = STORAGE_SERVICE_200_VERSIONS_RESPONSE
EXPECTED_400_RESPONSE_ON_INVALID_PARENT_PVT = {
    "code": 400, "reason": "Parent record is invalid. ['data.PVTTests: value is not a valid dict']",
}
EXPECTED_422_RESPONSE_ON_MISSING_SAMPLESANALYSESREPORT = {
    "code": 422, "reason": f"Records not found: ['{TEST_SAMPLESANALYSESREPORT_ID}']",
}

ERROR_TITLE = "Request can't be processed due to missing referenced records."
ERROR_DETAILS = f"Fields checked: ['ParentSamplesAnalysesReports']. Records not found: ['{TEST_SAMPLESANALYSESREPORT_ID}']"
EXPECTED_422_RESPONSE_ON_MISSING_SAMPLESANALYSESREPORT = {
    "code": 422,
    "reason": f"{ERROR_TITLE} {ERROR_DETAILS}",
}


CORING_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/coringreports"
ROCKSAMPLE_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/rocksamples"
ROCKSAMPLEANALYSIS_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/rocksampleanalyses"
PVT_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/pvtreports"
CCE_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/ccereports"
PVT_SOURCE_ENDPOINT_PATH = f"{PVT_ENDPOINT_PATH}/{TEST_PVT_ID}/source"
DIF_LIB_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/difflibreports"
TRANSPORT_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/transporttests"
COMPOSITIONALANALYSIS_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/compositionalanalysisreports"
MSS_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/multistageseparatortests"
SWELLING_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/swellingtests"
CVD_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/constantvolumedepletiontests"
STO_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/stocktankoilanalysisreports"
INTERFACIAL_TENSION_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/interfacialtensiontests"
VLE_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/vaporliquidequilibriumtests"
MCM_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/multiplecontactmiscibilitytests"
SLIMTUBETEST_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/slimtubetests"
SAMPLESANALYSES_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/samplesanalysesreport"
CAP_PRESSURE_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/capillarypressuretests"
RELATIVE_PERMEABILITY_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/relativepermeabilitytests"
FRACTIONATION_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/fractionationtests"
EXTRACTION_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/extractiontests"
PHYS_CHEM_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/physicalchemistrytests"
ELECTRICAL_PROPERTIES_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/electricalproperties"
ROCK_COMPRESSIBILITY_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/rockcompressibilities"
WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/watergasrelativepermeabilities"
FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/formationresistivityindexes"

RCA_DATA_ENDPOINT_PATH = f"{ROCKSAMPLEANALYSIS_ENDPOINT_PATH}/{TEST_ROCKSAMPLEANALYSIS_ID}/rca/data"
RCA_SOURCE_ENDPOINT_PATH = f"{ROCKSAMPLEANALYSIS_ENDPOINT_PATH}/{TEST_ROCKSAMPLEANALYSIS_ID}/rca/source"
CCE_DATA_ENDPOINT_PATH = f"{CCE_ENDPOINT_PATH}/{TEST_CCE_ID}/data"
CCE_SOURCE_ENDPOINT_PATH = f"{CCE_ENDPOINT_PATH}/{TEST_CCE_ID}/source"
DIF_LIB_DATA_ENDPOINT_PATH = f"{DIF_LIB_ENDPOINT_PATH}/{TEST_DL_ID}/data"
DIF_LIB_SOURCE_ENDPOINT_PATH = f"{DIF_LIB_ENDPOINT_PATH}/{TEST_DL_ID}/source"
TRANSPORT_DATA_ENDPOINT_PATH = f"{TRANSPORT_ENDPOINT_PATH}/{TEST_TRANSPORT_ID}/data"
TRANSPORT_SOURCE_ENDPOINT_PATH = f"{TRANSPORT_ENDPOINT_PATH}/{TEST_TRANSPORT_ID}/source"
COMPOSITIONALANALYSIS_DATA_ENDPOINT_PATH = f"{COMPOSITIONALANALYSIS_ENDPOINT_PATH}/{TEST_COMPOSITIONALANALYSIS_ID}/data"
COMPOSITIONALANALYSIS_SOURCE_ENDPOINT_PATH = f"{COMPOSITIONALANALYSIS_ENDPOINT_PATH}/{TEST_COMPOSITIONALANALYSIS_ID}/source"
MCM_DATA_ENDPOINT_PATH = f"{MCM_ENDPOINT_PATH}/{TEST_MCM_ID}/data"
MCM_SOURCE_ENDPOINT_PATH = f"{MCM_ENDPOINT_PATH}/{TEST_MCM_ID}/source"
MSS_DATA_ENDPOINT_PATH = f"{MSS_ENDPOINT_PATH}/{TEST_MSS_ID}/data"
MSS_SOURCE_ENDPOINT_PATH = f"{MSS_ENDPOINT_PATH}/{TEST_MSS_ID}/source"
SWELLING_DATA_ENDPOINT_PATH = f"{SWELLING_ENDPOINT_PATH}/{TEST_SWELLING_ID}/data"
SWELLING_SOURCE_ENDPOINT_PATH = f"{SWELLING_ENDPOINT_PATH}/{TEST_SWELLING_ID}/source"
CVD_DATA_ENDPOINT_PATH = f"{CVD_ENDPOINT_PATH}/{TEST_CVD_ID}/data"
CVD_SOURCE_ENDPOINT_PATH = f"{CVD_ENDPOINT_PATH}/{TEST_CVD_ID}/source"
WATERANALYSIS_ENDPOINT_PATH = f"/api/os-rafs-ddms/{API_VERSION}/wateranalysisreports"
STO_DATA_ENDPOINT_PATH = f"{STO_ENDPOINT_PATH}/{TEST_STO_ID}/data"
STO_SOURCE_ENDPOINT_PATH = f"{STO_ENDPOINT_PATH}/{TEST_STO_ID}/source"
WATERANALYSIS_DATA_ENDPOINT_PATH = f"{WATERANALYSIS_ENDPOINT_PATH}/{TEST_WATERANALYSIS_ID}/data"
WATERANALYSIS_SOURCE_ENDPOINT_PATH = f"{WATERANALYSIS_ENDPOINT_PATH}/{TEST_WATERANALYSIS_ID}/source"
INTERFACIAL_TENSION_DATA_ENDPOINT_PATH = f"{INTERFACIAL_TENSION_ENDPOINT_PATH}/{TEST_INTERFACIAL_TENSION_ID}/data"
INTERFACIAL_TENSION_SOURCE_ENDPOINT_PATH = f"{INTERFACIAL_TENSION_ENDPOINT_PATH}/{TEST_INTERFACIAL_TENSION_ID}/source"
VLE_DATA_ENDPOINT_PATH = f"{VLE_ENDPOINT_PATH}/{TEST_VLE_ID}/data"
VLE_SOURCE_ENDPOINT_PATH = f"{VLE_ENDPOINT_PATH}/{TEST_VLE_ID}/source"
SLIMTUBE_DATA_ENDPOINT_PATH = f"{SLIMTUBETEST_ENDPOINT_PATH}/{TEST_SLIMTUBETEST_ID}/data"
SLIMTUBE_SOURCE_ENDPOINT_PATH = f"{SLIMTUBETEST_ENDPOINT_PATH}/{TEST_SLIMTUBETEST_ID}/source"
RELATIVE_PERMEABILITY_DATA_ENDPOINT_PATH = f"{RELATIVE_PERMEABILITY_ENDPOINT_PATH}/{TEST_RELATIVE_PERMEABILITY_ID}/data"
RELATIVE_PERMEABILITY_SOURCE_ENDPOINT_PATH = f"{RELATIVE_PERMEABILITY_ENDPOINT_PATH}/{TEST_RELATIVE_PERMEABILITY_ID}/source"
CAP_PRESSURE_DATA_ENDPOINT_PATH = f"{CAP_PRESSURE_ENDPOINT_PATH}/{TEST_CAP_PRESSURE_ID}/data"
FRACTIONATION_DATA_ENDPOINT_PATH = f"{FRACTIONATION_ENDPOINT_PATH}/{TEST_FRACTIONATION_ID}/data"
FRACTIONATION_SOURCE_ENDPOINT_PATH = f"{FRACTIONATION_ENDPOINT_PATH}/{TEST_FRACTIONATION_ID}/source"
EXTRACTION_DATA_ENDPOINT_PATH = f"{EXTRACTION_ENDPOINT_PATH}/{TEST_EXTRACTION_ID}/data"
EXTRACTION_SOURCE_ENDPOINT_PATH = f"{EXTRACTION_ENDPOINT_PATH}/{TEST_EXTRACTION_ID}/source"
PHYS_CHEM_DATA_ENDPOINT_PATH = f"{PHYS_CHEM_ENDPOINT_PATH}/{TEST_PHYS_CHEM_ID}/data"
PHYS_CHEM_SOURCE_ENDPOINT_PATH = f"{PHYS_CHEM_ENDPOINT_PATH}/{TEST_PHYS_CHEM_ID}/source"
WATER_GAS_REL_PERM_DATA_ENDPOINT_PATH = f"{WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH}/{TEST_WATER_GAS_RELATIVE_PERMEABILITY_ID}/data"
WATER_GAS_REL_PERM_SOURCE_ENDPOINT_PATH = f"{WATER_GAS_RELATIVE_PERMEABILITY_ENDPOINT_PATH}/{TEST_WATER_GAS_RELATIVE_PERMEABILITY_ID}/source"
ROCK_COMPRESSIBILITY_DATA_ENDPOINT_PATH = f"{ROCK_COMPRESSIBILITY_ENDPOINT_PATH}/{TEST_ROCK_COMPRESSIBILITY_ID}/data"
ROCK_COMPRESSIBILITY_SOURCE_ENDPOINT_PATH = f"{ROCK_COMPRESSIBILITY_ENDPOINT_PATH}/{TEST_ROCK_COMPRESSIBILITY_ID}/source"
ELECTRICAL_PROPERTIES_DATA_ENDPOINT_PATH = f"{ELECTRICAL_PROPERTIES_ENDPOINT_PATH}/{TEST_ELECTRICAL_PROPERTIES_ID}/data"
ELECTRICAL_PROPERTIES_SOURCE_ENDPOINT_PATH = f"{ELECTRICAL_PROPERTIES_ENDPOINT_PATH}/{TEST_ELECTRICAL_PROPERTIES_ID}/source"
FORMATION_RESISTIVITY_INDEX_DATA_ENDPOINT_PATH = f"{FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH}/{TEST_FORMATION_RESISTIVITY_INDEX_ID}/data"
FORMATION_RESISTIVITY_INDEX_SOURCE_ENDPOINT_PATH = f"{FORMATION_RESISTIVITY_INDEX_ENDPOINT_PATH}/{TEST_FORMATION_RESISTIVITY_INDEX_ID}/source"


class BulkDatasetId(NamedTuple):
    RCA = f"{PARTITION}:{FILE_GENERIC_TYPE}:routine-core-analysis-{TEST_DATASET_UID}"
    CCE = f"{PARTITION}:{FILE_GENERIC_TYPE}:constant-composition-expansion-{TEST_DATASET_UID}"
    DIF_LIB = f"{PARTITION}:{FILE_GENERIC_TYPE}:differential-liberation-{TEST_DATASET_UID}"
    TRANSPORT = f"{PARTITION}:{FILE_GENERIC_TYPE}:transport-test-{TEST_DATASET_UID}"
    MCM = f"{PARTITION}:{FILE_GENERIC_TYPE}:multiple-contact-miscibility-{TEST_DATASET_UID}"
    MSS = f"{PARTITION}:{FILE_GENERIC_TYPE}:multi-stage-separator-{TEST_DATASET_UID}"
    CA = f"{PARTITION}:{FILE_GENERIC_TYPE}:compositionalanalysis-{TEST_DATASET_UID}"
    SWELLING = f"{PARTITION}:{FILE_GENERIC_TYPE}:swelling-{TEST_DATASET_UID}"
    CVD = f"{PARTITION}:{FILE_GENERIC_TYPE}:constantvolumedepletiontest-{TEST_DATASET_UID}"
    STO = f"{PARTITION}:{FILE_GENERIC_TYPE}:stoanalysis-{TEST_DATASET_UID}"
    WA = f"{PARTITION}:{FILE_GENERIC_TYPE}:wateranalysis-{TEST_DATASET_UID}"
    IT = f"{PARTITION}:{FILE_GENERIC_TYPE}:interfacialtension-{TEST_DATASET_UID}"
    VLE = f"{PARTITION}:{FILE_GENERIC_TYPE}:vaporliquidequilibriumtest-{TEST_DATASET_UID}"
    SLIMTUBE = f"{PARTITION}:{FILE_GENERIC_TYPE}:slimtube-test-{TEST_DATASET_UID}"
    RELATIVE_PERMEABILITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:relative-permeability-{TEST_DATASET_UID}"
    CAP_PRESSURE = f"{PARTITION}:{FILE_GENERIC_TYPE}:capillary-pressure-test-{TEST_DATASET_UID}"
    FRACTIONATION = f"{PARTITION}:{FILE_GENERIC_TYPE}:fractionation-{TEST_DATASET_UID}"
    EXTRACTION = f"{PARTITION}:{FILE_GENERIC_TYPE}:extraction-{TEST_DATASET_UID}"
    PHYS_CHEM = f"{PARTITION}:{FILE_GENERIC_TYPE}:physical-chemistry-test-{TEST_DATASET_UID}"
    WATER_GAS_RELATIVE_PERMEABILITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:water-gas-relative-permeability-test-{TEST_DATASET_UID}"
    ROCK_COMPRESSIBILITY = f"{PARTITION}:{FILE_GENERIC_TYPE}:rock-compressibility-{TEST_DATASET_UID}"
    ELECTRICAL_PROPERTIES = f"{PARTITION}:{FILE_GENERIC_TYPE}:electricalproperties-{TEST_DATASET_UID}"
    FORMATION_RESISTIVITY_INDEX = f"{PARTITION}:{FILE_GENERIC_TYPE}:formationresistivityindexes-{TEST_DATASET_UID}"
