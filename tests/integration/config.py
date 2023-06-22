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

from pathlib import Path
from typing import NamedTuple

CONFIG = {}

UPLOADED_FILES = [
    "opendes:dataset--File.Generic:File_1:",
    "opendes:dataset--File.Generic:File_2:",
    "opendes:dataset--File.Generic:File_3:",
]
SCHEMA_VERSION = "1.0.0"
PARQUET_HEADERS = {"Content-Type": "application/x-parquet"}
ACCEPT_HEADERS = "*/*;version={version}"

DATA_DIR = Path("tests", "integration", "data")


class DataFiles(NamedTuple):
    RSA = "rsa/rsa.json"
    RCA = "rsa/rca.json"
    RCA_PARQUET = "rsa/rca.parquet"
    RCA_WRONG_ID = "rsa/rca_wrong_ids.json"
    RCA_MANDATORY_ATTRIBUTES_PARQUET = "rsa/missing_attributes_rca.parquet"
    RS = "rocksample.json"
    CORING = "coring.json"
    SAR = "samples_analyses_report/sar.json"

    PVT = "pvt.json"

    # PVT tests
    CCE = "cce/cce.json"
    CCE_DATA = "cce/cce_data.json"
    CCE_WRONG_ID = "cce/cce_wrong_ids.json"
    DIF_LIB = "dif_lib/dif_lib.json"
    DIF_LIB_DATA = "dif_lib/dif_lib_data.json"
    DIF_LIB_WRONG_ID = "dif_lib/dif_lib_wrong_ids.json"
    CA = "compositional_analysis/ca.json"
    CA_DATA = "compositional_analysis/ca_data.json"
    CA_WRONG_ID = "compositional_analysis/ca_wrong_ids.json"
    CVD = "constant_volume_depletion/cvd.json"
    CVD_DATA = "constant_volume_depletion/cvd_data.json"
    CVD_WRONG_ID = "constant_volume_depletion/cvd_wrong_ids.json"
    IT = "interfacial_tension/it.json"
    IT_DATA = "interfacial_tension/it_data.json"
    IT_WRONG_ID = "interfacial_tension/it_wrong_ids.json"
    MSS = "multi_stage_separator/mss.json"
    MSS_DATA = "multi_stage_separator/mss_data.json"
    MSS_WRONG_ID = "multi_stage_separator/mss_wrong_ids.json"
    MCM = "multiple_contact_miscibility/mcm.json"
    MCM_DATA = "multiple_contact_miscibility/mcm_data.json"
    MCM_WRONG_ID = "multiple_contact_miscibility/mcm_wrong_ids.json"
    SLIM_TUBE = "slim_tube/st.json"
    SLIM_TUBE_DATA = "slim_tube/st_data.json"
    SLIM_TUBE_WRONG_ID = "slim_tube/st_wrong_ids.json"
    STOA = "stock_tank_oil_analysis/stoa.json"
    STOA_DATA = "stock_tank_oil_analysis/stoa_data.json"
    STOA_WRONG_ID = "stock_tank_oil_analysis/stoa_wrong_ids.json"
    ST = "swelling_test/st.json"
    ST_DATA = "swelling_test/st_data.json"
    ST_WRONG_ID = "swelling_test/st_wrong_ids.json"
    TT = "transport_test/tt.json"
    TT_DATA = "transport_test/tt_data.json"
    TT_WRONG_ID = "transport_test/tt_wrong_ids.json"
    VLE = "vapor_liquid_equilibrium/vle.json"
    VLE_DATA = "vapor_liquid_equilibrium/vle_data.json"
    VLE_WRONG_ID = "vapor_liquid_equilibrium/vle_wrong_ids.json"
    WA = "water_analysis/wa.json"
    WA_DATA = "water_analysis/wa_data.json"
    WA_WRONG_ID = "water_analysis/wa_wrong_ids.json"


class DataTemplates(NamedTuple):
    ID_DATASET = "opendes:dataset--File.Generic:"
    ID_CORING = f"opendes:master-data--Coring:"
    ID_RS = "opendes:master-data--RockSample:"
    ID_RSA = "opendes:work-product-component--RockSampleAnalysis:"
    ID_SAR = "opendes:work-product-component--SamplesAnalysesReport:"
    ID_PVT = "opendes:work-product-component--PVT:"

    # PVT tests
    ID_CCE = "opendes:work-product-component--ConstantCompositionExpansionTest:"
    ID_DIF_LIB = "opendes:work-product-component--DifferentialLiberationTest:"
    ID_CA = "opendes:work-product-component--CompositionalAnalysisTest:"
    ID_CVD = "opendes:work-product-component--ConstantVolumeDepletionTest:"
    ID_IT = "opendes:work-product-component--InterfacialTensionTest:"
    ID_MSS = "opendes:work-product-component--MultiStageSeparatorTest:"
    ID_MCM = "opendes:work-product-component--MultipleContactMiscibilityTest:"
    ID_SLIM_TUBE = "opendes:work-product-component--SlimTubeTest:"
    ID_STOA = "opendes:work-product-component--StockTankOilAnalysisTest:"
    ID_ST = "opendes:work-product-component--SwellingTest:"
    ID_TT = "opendes:work-product-component--TransportTest:"
    ID_VLE = "opendes:work-product-component--VaporLiquidEquilibriumTest:"
    ID_WA = "opendes:work-product-component--WaterAnalysisTest:"


class DataTypes(NamedTuple):
    RSA = "rsa"
    RS = "rs"
    CORING = "coring"
    PVT = "pvt"
    DIF_LIB = "dif_lib"
    CCE = "cce"
    CA = "ca"
    CVD = "cvd"
    IT = "it"
    MSS = "mss"
    MCM = "mcm"
    SLIM_TUBE = "slim_tube"
    STOA = "stoa"
    ST = "st"
    TT = "tt"
    VLE = "vle"
    WA = "wa"
    SAR = "sar"


class DatasetPrefix:
    RCA = "routine-core-analysis"
    DIF_LIB = "differential-liberation"
    CCE = "constant-composition-expansion"
    CA = "compositionalanalysis"
    CVD = "constantvolumedepletiontest"
    IT = "interfacialtension"
    MSS = "multi-stage-separator"
    MCM = "multiple-contact-miscibility"
    SLIM_TUBE = "slimtube-test"
    STOA = "stoanalysis"
    ST = "swelling"
    TT = "transport-test"
    VLE = "vaporliquidequilibriumtest"
    WA = "wateranalysis"
    SAR = "sar"
