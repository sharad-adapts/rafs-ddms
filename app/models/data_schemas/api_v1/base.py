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

from app.models.data_schemas.api_v1.cce_data_model import Model as CCEModel
from app.models.data_schemas.api_v1.compositionalanalysis_data_model import Model as CompositionalAnalysisModel
from app.models.data_schemas.api_v1.cvd_data_model import Model as CVDModel
from app.models.data_schemas.api_v1.dif_lib_data_model import Model as DLModel
from app.models.data_schemas.api_v1.rca_data_model import Model as RCAModel
from app.models.data_schemas.api_v1.transport_test_data_model import Model as TransportTestModel
from app.models.data_schemas.api_v1.mss_data_model import Model as MSSModel
from app.models.data_schemas.api_v1.water_analysis_data_model import Model as WaterAnalysisModel
from app.models.data_schemas.api_v1.sto_data_model import Model as StockTankOilAnalysisModel
from app.models.data_schemas.api_v1.swelling_test_data_model import Model as SwellingTestModel
from app.models.data_schemas.api_v1.interfacial_tension_data_model import Model as InterfacialTensionModel
from app.models.data_schemas.api_v1.mcm_data_model import Model as MCMModel
from app.models.data_schemas.api_v1.relative_permeability_data_model import Model as RelativePermeabilityModel
from app.models.data_schemas.api_v1.vle_data_model import Model as VLEModel
from app.models.data_schemas.api_v1.slimtube_data_model import Model as SlimTubeModel
from app.models.data_schemas.api_v1.cap_pressure_data_model import Model as CapPressureModel
from app.models.data_schemas.api_v1.fractionation_data_model import Model as FractionationModel
from app.models.data_schemas.api_v1.extraction_data_model import Model as ExtractionModel
from app.models.data_schemas.api_v1.physchem_data_model import Model as PhysChemModel
from app.models.data_schemas.api_v1.water_gas_relative_permeability_data_model import Model as WaterGasRelativePermeabilityModel
from app.models.data_schemas.api_v1.rock_compressibility_data_model import Model as RockCompressibilityModel
from app.models.data_schemas.api_v1.electrical_properties_data_model import Model as ElectricalPropertiesModel_API_V1
from app.models.data_schemas.api_v1.formation_resistivity_index_data_model import Model as FormationResistivityIndexModel
from app.resources.paths import CommonRelativePathsV1
from app.models.data_schemas.version import ContentSchemaVersion


RCA_MODELS = {
    ContentSchemaVersion.V_1_0_0: RCAModel
}
CCE_MODELS = {
    ContentSchemaVersion.V_1_0_0: CCEModel
}
DIFF_LIB_MODELS = {
    ContentSchemaVersion.V_1_0_0: DLModel
}
TRANSPORT_TEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: TransportTestModel
}
MSS_MODELS = {
    ContentSchemaVersion.V_1_0_0: MSSModel
}
COMPOSITIONAL_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: CompositionalAnalysisModel
}
SWELLING_TEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: SwellingTestModel
}
CVD_MODELS = {
    ContentSchemaVersion.V_1_0_0: CVDModel
}
WATER_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: WaterAnalysisModel
}
INTERFACIAL_TENSION_MODELS = {
    ContentSchemaVersion.V_1_0_0: InterfacialTensionModel
}
STO_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: StockTankOilAnalysisModel
}
VLE_MODELS = {
    ContentSchemaVersion.V_1_0_0: VLEModel
}
MCM_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: MCMModel
}
SLIMTUBETEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: SlimTubeModel
}
RELATIVE_PERMEABILITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: RelativePermeabilityModel
}
CAP_PRESSURE_MODELS = {
    ContentSchemaVersion.V_1_0_0: CapPressureModel
}
FRACTIONATION_MODELS = {
    ContentSchemaVersion.V_1_0_0: FractionationModel
}
EXTRACTION_MODELS = {
    ContentSchemaVersion.V_1_0_0: ExtractionModel,
}
PHYS_CHEM_MODELS = {
    ContentSchemaVersion.V_1_0_0: PhysChemModel
}
WATER_GAS_RELATIVE_PERMEABILITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: WaterGasRelativePermeabilityModel
}
ROCK_COMPRESSIBILITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: RockCompressibilityModel
}
ELECTRICAL_PROPERTIES_MODELS_API_V1 = {
    ContentSchemaVersion.V_1_0_0: ElectricalPropertiesModel_API_V1,
}
FORMATION_RESISTIVITY_INDEX_MODELS = {
    ContentSchemaVersion.V_1_0_0: FormationResistivityIndexModel,
}

common_relative_paths_api_v1 = CommonRelativePathsV1()
PATH_TO_DATA_MODEL_VERSIONS_API_V1 = {
    common_relative_paths_api_v1.ROUTINECOREANALYSIS: RCA_MODELS,
    common_relative_paths_api_v1.CCE: CCE_MODELS,
    common_relative_paths_api_v1.DIF_LIB: DIFF_LIB_MODELS,
    common_relative_paths_api_v1.TRANSPORT_TEST: TRANSPORT_TEST_MODELS,
    common_relative_paths_api_v1.MSS: MSS_MODELS,
    common_relative_paths_api_v1.COMPOSITIONAL_ANALYSIS: COMPOSITIONAL_ANALYSIS_MODELS,
    common_relative_paths_api_v1.SWELLING: SWELLING_TEST_MODELS,
    common_relative_paths_api_v1.CVD: CVD_MODELS,
    common_relative_paths_api_v1.WATER_ANALYSIS: WATER_ANALYSIS_MODELS,
    common_relative_paths_api_v1.INTERFACIAL_TENSION: INTERFACIAL_TENSION_MODELS,
    common_relative_paths_api_v1.STO_ANALYSIS: STO_ANALYSIS_MODELS,
    common_relative_paths_api_v1.VLE: VLE_MODELS,
    common_relative_paths_api_v1.MCM: MCM_ANALYSIS_MODELS,
    common_relative_paths_api_v1.SLIMTUBETEST: SLIMTUBETEST_MODELS,
    common_relative_paths_api_v1.RELATIVE_PERMEABILITY: RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths_api_v1.CAP_PRESSURE: CAP_PRESSURE_MODELS,
    common_relative_paths_api_v1.FRACTIONATION: FRACTIONATION_MODELS,
    common_relative_paths_api_v1.EXTRACTION: EXTRACTION_MODELS,
    common_relative_paths_api_v1.PHYS_CHEM: PHYS_CHEM_MODELS,
    common_relative_paths_api_v1.WATER_GAS_RELATIVE_PERMEABILITY: WATER_GAS_RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths_api_v1.ROCK_COMPRESSIBILITY: ROCK_COMPRESSIBILITY_MODELS,
    common_relative_paths_api_v1.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS_API_V1,
    common_relative_paths_api_v1.FORMATION_RESISTIVITY_INDEX: FORMATION_RESISTIVITY_INDEX_MODELS,
}
