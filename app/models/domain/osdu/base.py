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

from app.core.config import get_app_settings

from .MDCoring100 import Coring
from .MDRockSample100 import RockSample
from .WPCCompositionalAnalysis100 import CompositionalAnalysis
from .WPCCCE100 import ConstantCompositionExpansionTest
from .WPCConstantVolumeDepletionTest100 import ConstantVolumeDepletionTest
from .WPCDifLib100 import DifferentialLiberationTest
from .WPCMSS100 import MultiStageSeparatorTest
from .WPCPVT100 import PVT
from .WPCRockSampleAnalysis110 import RockSampleAnalysis
from .WPCSlimTubeTest100 import SlimTubeTest
from .WPCTransportTest100 import TransportTest
from .WPCSwellingTest100 import SwellingTest
from .WPCWaterAnalysis100 import WaterAnalysisTest
from .WPCSTO100 import StockTankOilAnalysisTest
from .WPCInterfacialTension100 import InterfacialTensionTest
from .WPCVLE100 import VaporLiquidEquilibriumTest
from .WPCMCM100 import MultipleContactMiscibilityTest
from .WPCSamplesAnalysesReport100 import SamplesAnalysesReport

settings = get_app_settings()

CORING_KIND = f"{settings.schema_authority}:wks:master-data--Coring:1.0.0"
ROCKSAMPLE_KIND = f"{settings.schema_authority}:wks:master-data--RockSample:1.0.0"
ROCKSAMPLEANALYSIS_KIND = f"{settings.schema_authority}:wks:work-product-component--RockSampleAnalysis:1.1.0"
PVT_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--PVT:1.0.0"
CCE_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--ConstantCompositionExpansionTest:1.0.0"
DIF_LIB_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--DifferentialLiberationTest:1.0.0"
TRANSPORT_TEST_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--TransportTest:1.0.0"
COMPOSITIONAL_ANALYSIS_KIND = (
    f"{settings.custom_schema_authority}:wks:work-product-component--CompositionalAnalysisTest:1.0.0"
)
MSS_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--MultiStageSeparatorTest:1.0.0"
SWELLING_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--SwellingTest:1.0.0"
CVD_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--ConstantVolumeDepletionTest:1.0.0"
WATER_ANALYSYS_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--WaterAnalysisTest:1.0.0"
STO_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--StockTankOilAnalysisTest:1.0.0"
INTERFACIAL_TENSION_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--InterfacialTensionTest:1.0.0"
VLE_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--VaporLiquidEquilibriumTest:1.0.0"
MCM_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--MultipleContactMiscibilityTest:1.0.0"
SLIMTUBETEST_KIND = f"{settings.custom_schema_authority}:wks:work-product-component--SlimTubeTest:1.0.0"

SAMPLES_ANALYSES_REPORT_KIND = f"{settings.xom_schema_authority}:{settings.xom_source}:work-product-component--SamplesAnalysesReport:1.0.0"

IMPLEMENTED_MODELS = {
    CORING_KIND: Coring,
    ROCKSAMPLE_KIND: RockSample,
    PVT_KIND: PVT,
    ROCKSAMPLEANALYSIS_KIND: RockSampleAnalysis,
    CCE_KIND: ConstantCompositionExpansionTest,
    DIF_LIB_KIND: DifferentialLiberationTest,
    TRANSPORT_TEST_KIND: TransportTest,
    COMPOSITIONAL_ANALYSIS_KIND: CompositionalAnalysis,
    MSS_KIND: MultiStageSeparatorTest,
    SWELLING_KIND: SwellingTest,
    CVD_KIND: ConstantVolumeDepletionTest,
    WATER_ANALYSYS_KIND: WaterAnalysisTest,
    STO_KIND: StockTankOilAnalysisTest,
    INTERFACIAL_TENSION_KIND: InterfacialTensionTest,
    VLE_KIND: VaporLiquidEquilibriumTest,
    MCM_KIND: MultipleContactMiscibilityTest,
    SLIMTUBETEST_KIND: SlimTubeTest,
    SAMPLES_ANALYSES_REPORT_KIND: SamplesAnalysesReport,
}
