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

from typing import NamedTuple

from app.models.data_schemas.cce_data_model import Model as CCEModel
from app.models.data_schemas.compositionalanalysis_data_model import Model as CompositionalAnalysisModel
from app.models.data_schemas.cvd_data_model import Model as CVDModel
from app.models.data_schemas.dif_lib_data_model import Model as DLModel
from app.models.data_schemas.rca_data_model import Model as RCAModel
from app.models.data_schemas.transport_test_data_model import Model as TransportTestModel
from app.models.data_schemas.mss_data_model import Model as MSSModel
from app.models.data_schemas.water_analysis_data_model import Model as WaterAnalysisModel
from app.models.data_schemas.sto_data_model import Model as StockTankOilAnalysisModel
from app.models.data_schemas.swelling_test_data_model import Model as SwellingTestModel
from app.models.data_schemas.interfacial_tension_data_model import Model as InterfacialTensionModel
from app.models.data_schemas.mcm_data_model import Model as MCMModel
from app.models.data_schemas.relative_permeability_data_model import Model as RelativePermeabilityModel
from app.models.data_schemas.vle_data_model import Model as VLEModel
from app.models.data_schemas.slimtube_data_model import Model as SlimTubeModel
from app.models.data_schemas.cap_pressure_data_model import Model as CapPressureModel
from app.models.data_schemas.fractionation_data_model import Model as FractionationModel
from app.models.data_schemas.extraction_data_model import Model as ExtractionModel
from app.models.data_schemas.physchem_data_model import Model as PhysChemModel
from app.models.data_schemas.water_gas_relative_permeability_data_model import Model as WaterGasRelativePermeabilityModel
from app.resources.paths import CommonRelativePaths

class ContentShemaVersion(NamedTuple):
    V_1_0_0 = "1.0.0"

RCA_MODELS = {
    ContentShemaVersion.V_1_0_0: RCAModel
}
CCE_MODELS = {
    ContentShemaVersion.V_1_0_0: CCEModel
}
DIFF_LIB_MODELS = {
    ContentShemaVersion.V_1_0_0: DLModel
}
TRANSPORT_TEST_MODELS = {
    ContentShemaVersion.V_1_0_0: TransportTestModel
}
MSS_MODELS = {
    ContentShemaVersion.V_1_0_0: MSSModel
}
COMPOSITIONAL_ANALYSIS_MODELS = {
    ContentShemaVersion.V_1_0_0: CompositionalAnalysisModel
}
SWELLING_TEST_MODELS = {
    ContentShemaVersion.V_1_0_0: SwellingTestModel
}
CVD_MODELS = {
    ContentShemaVersion.V_1_0_0: CVDModel
}
WATER_ANALYSIS_MODELS = {
    ContentShemaVersion.V_1_0_0: WaterAnalysisModel
}
INTERFACIAL_TENSION_MODELS = {
    ContentShemaVersion.V_1_0_0: InterfacialTensionModel
}
STO_ANALYSIS_MODELS = {
    ContentShemaVersion.V_1_0_0: StockTankOilAnalysisModel
}
VLE_MODELS = {
    ContentShemaVersion.V_1_0_0: VLEModel
}
MCM_ANALYSIS_MODELS = {
    ContentShemaVersion.V_1_0_0: MCMModel
}
SLIMTUBETEST_MODELS = {
    ContentShemaVersion.V_1_0_0: SlimTubeModel
}
RELATIVE_PERMEABILITY_MODELS = {
    ContentShemaVersion.V_1_0_0: RelativePermeabilityModel
}
CAP_PRESSURE_MODELS = {
    ContentShemaVersion.V_1_0_0: CapPressureModel
}
FRACTIONATION_MODELS = {
    ContentShemaVersion.V_1_0_0: FractionationModel
}
EXTRACTION_MODELS = {
    ContentShemaVersion.V_1_0_0: ExtractionModel,
}
PHYS_CHEM_MODELS = {
    ContentShemaVersion.V_1_0_0: PhysChemModel
}
WATER_GAS_RELATIVE_PERMEABILITY_MODELS = {
    ContentShemaVersion.V_1_0_0: WaterGasRelativePermeabilityModel
}
PATH_TO_DATA_MODEL_VERSIONS = {
    CommonRelativePaths.ROUTINECOREANALYSIS: RCA_MODELS,
    CommonRelativePaths.CCE: CCE_MODELS,
    CommonRelativePaths.DIF_LIB: DIFF_LIB_MODELS,
    CommonRelativePaths.TRANSPORT_TEST: TRANSPORT_TEST_MODELS,
    CommonRelativePaths.MSS: MSS_MODELS,
    CommonRelativePaths.COMPOSITIONAL_ANALYSIS: COMPOSITIONAL_ANALYSIS_MODELS,
    CommonRelativePaths.SWELLING: SWELLING_TEST_MODELS,
    CommonRelativePaths.CVD: CVD_MODELS,
    CommonRelativePaths.WATER_ANALYSIS: WATER_ANALYSIS_MODELS,
    CommonRelativePaths.INTERFACIAL_TENSION: INTERFACIAL_TENSION_MODELS,
    CommonRelativePaths.STO_ANALYSIS: STO_ANALYSIS_MODELS,
    CommonRelativePaths.VLE: VLE_MODELS,
    CommonRelativePaths.MCM: MCM_ANALYSIS_MODELS,
    CommonRelativePaths.SLIMTUBETEST: SLIMTUBETEST_MODELS,
    CommonRelativePaths.RELATIVE_PERMEABILITY: RELATIVE_PERMEABILITY_MODELS,
    CommonRelativePaths.CAP_PRESSURE: CAP_PRESSURE_MODELS,
    CommonRelativePaths.FRACTIONATION: FRACTIONATION_MODELS,
    CommonRelativePaths.EXTRACTION: EXTRACTION_MODELS,
    CommonRelativePaths.PHYS_CHEM: PHYS_CHEM_MODELS,
    CommonRelativePaths.WATER_GAS_RELATIVE_PERMEABILITY: WATER_GAS_RELATIVE_PERMEABILITY_MODELS,
}
