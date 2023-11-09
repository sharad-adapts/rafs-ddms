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
from app.models.data_schemas.cap_pressure_data_model import Model as CapPressureModel_API_V1
from app.models.data_schemas.api_v2.cap_pressure_data_model import Model as CapPressureModel_API_V2
from app.models.data_schemas.cec_content_model import Model as CECContentModel
from app.models.data_schemas.fractionation_data_model import Model as FractionationModel
from app.models.data_schemas.extraction_data_model import Model as ExtractionModel
from app.models.data_schemas.physchem_data_model import Model as PhysChemModel
from app.models.data_schemas.water_gas_relative_permeability_data_model import Model as WaterGasRelativePermeabilityModel
from app.models.data_schemas.rock_compressibility_data_model import Model as RockCompressibilityModel
from app.models.data_schemas.electrical_properties_data_model import Model as ElectricalPropertiesModel_API_V1
from app.models.data_schemas.api_v2.electrical_properties_data_model import Model as ElectricalPropertiesModel_API_V2
from app.models.data_schemas.formation_resistivity_index_data_model import Model as FormationResistivityIndexModel
from app.models.data_schemas.nmr_data_model import Model as NMRModel
from app.models.data_schemas.multiple_salinity_data_model import Model as MultipleSalinityModel
from app.models.data_schemas.gcms_alkanes_data_model import Model as GCMSAlkanesModel
from app.models.data_schemas.mercury_injection_analysis_data_model import Model as MercuryInjectionModel
from app.models.data_schemas.gcms_aromatics_data_model import Model as GCMSAromaticsModel
from app.models.data_schemas.gcms_ratios_data_model import Model as GCMSRatiosModel
from app.models.data_schemas.gas_chromatography_data_model import Model as GasChromatographyModel
from app.models.data_schemas.gas_composition_data_model import Model as GasCompositionModel
from app.models.data_schemas.isotope_analysis_data_model import Model as IsotopeAnalysisModel
from app.models.data_schemas.bulk_pyrolysis_data_model import Model as BulkPyrolysisModel
from app.models.data_schemas.core_gamma_data_model import Model as CoreGammaModel
from app.models.data_schemas.triaxial_test_data_model import Model as TriaxialTestModel
from app.models.data_schemas.uniaxial_test_data_model import Model as UniaxialTestModel
from app.models.data_schemas.gcmsms_data_model import Model as GCMSMS_Model
from app.resources.paths import COMMON_RELATIVE_PATHS


class ContentSchemaVersion(NamedTuple):
    V_1_0_0 = "1.0.0"


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
CAP_PRESSURE_MODELS_API_V1 = {
    ContentSchemaVersion.V_1_0_0: CapPressureModel_API_V1
}
CAP_PRESSURE_MODELS_API_V2 = {
    ContentSchemaVersion.V_1_0_0: CapPressureModel_API_V2
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
ELECTRICAL_PROPERTIES_MODELS_API_V2 = {
    ContentSchemaVersion.V_1_0_0: ElectricalPropertiesModel_API_V2,
}
FORMATION_RESISTIVITY_INDEX_MODELS = {
    ContentSchemaVersion.V_1_0_0: FormationResistivityIndexModel,
}
NMR_MODELS = {
    ContentSchemaVersion.V_1_0_0: NMRModel,
}
MULTIPLE_SALINITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: MultipleSalinityModel,
}
GCMS_ALKANES_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSAlkanesModel,
}
MERCURY_INJECTION_MODELS = {
    ContentSchemaVersion.V_1_0_0: MercuryInjectionModel,
}
GCMS_AROMATICS_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSAromaticsModel,
}
GCMS_RATIOS_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSRatiosModel,
}
GAS_CHROMATOGRAPHY_MODELS = {
    ContentSchemaVersion.V_1_0_0: GasChromatographyModel,
}
GAS_COMPOSITION_MODELS = {
    ContentSchemaVersion.V_1_0_0: GasCompositionModel,
}
ISOTOPE_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: IsotopeAnalysisModel,
}
BULK_PYROLYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: BulkPyrolysisModel,
}
CORE_GAMMA_MODELS = {
    ContentSchemaVersion.V_1_0_0: CoreGammaModel,
}
UNIAXIAL_TEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: UniaxialTestModel,
}
GCMSMS_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSMS_Model,
}
CEC_CONTENT_MODELS = {
    ContentSchemaVersion.V_1_0_0: CECContentModel
}
TRIAXIAL_TEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: TriaxialTestModel
}

common_relative_paths_api_v1 = COMMON_RELATIVE_PATHS["v1"]()
common_relative_paths_api_v2 = COMMON_RELATIVE_PATHS["v2"]()

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
    common_relative_paths_api_v1.CAP_PRESSURE: CAP_PRESSURE_MODELS_API_V1,
    common_relative_paths_api_v1.FRACTIONATION: FRACTIONATION_MODELS,
    common_relative_paths_api_v1.EXTRACTION: EXTRACTION_MODELS,
    common_relative_paths_api_v1.PHYS_CHEM: PHYS_CHEM_MODELS,
    common_relative_paths_api_v1.WATER_GAS_RELATIVE_PERMEABILITY: WATER_GAS_RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths_api_v1.ROCK_COMPRESSIBILITY: ROCK_COMPRESSIBILITY_MODELS,
    common_relative_paths_api_v1.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS_API_V1,
    common_relative_paths_api_v1.FORMATION_RESISTIVITY_INDEX: FORMATION_RESISTIVITY_INDEX_MODELS,
}

PATH_TO_DATA_MODEL_VERSIONS_API_V2 = {
    common_relative_paths_api_v2.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS_API_V2,
    common_relative_paths_api_v2.CAP_PRESSURE: CAP_PRESSURE_MODELS_API_V2,
    common_relative_paths_api_v2.NMR: NMR_MODELS,
    common_relative_paths_api_v2.MULTIPLE_SALINITY: MULTIPLE_SALINITY_MODELS,
    common_relative_paths_api_v2.GCMS_ALKANES: GCMS_ALKANES_MODELS,
    common_relative_paths_api_v2.MERCURY_INJECTION: MERCURY_INJECTION_MODELS,
    common_relative_paths_api_v2.GCMS_AROMATICS: GCMS_AROMATICS_MODELS,
    common_relative_paths_api_v2.GCMS_RATIOS: GCMS_RATIOS_MODELS,
    common_relative_paths_api_v2.GAS_CHROMATOGRAPHY: GAS_CHROMATOGRAPHY_MODELS,
    common_relative_paths_api_v2.GAS_COMPOSITION: GAS_COMPOSITION_MODELS,
    common_relative_paths_api_v2.ISOTOPE_ANALYSIS: ISOTOPE_ANALYSIS_MODELS,
    common_relative_paths_api_v2.BULK_PYROLYSIS: BULK_PYROLYSIS_MODELS,
    common_relative_paths_api_v2.CORE_GAMMA: CORE_GAMMA_MODELS,
    common_relative_paths_api_v2.UNIAXIAL_TEST: UNIAXIAL_TEST_MODELS,
    common_relative_paths_api_v2.GCMSMS_ANALYSIS: GCMSMS_ANALYSIS_MODELS,
    common_relative_paths_api_v2.CEC_CONTENT: CEC_CONTENT_MODELS,
    common_relative_paths_api_v2.TRIAXIAL_TEST: TRIAXIAL_TEST_MODELS,
}

PATHS_TO_DATA_MODEL = {
    "v1": PATH_TO_DATA_MODEL_VERSIONS_API_V1,
    "v2": PATH_TO_DATA_MODEL_VERSIONS_API_V2
}

ALL_PATHS_TO_DATA_MODEL = {**PATH_TO_DATA_MODEL_VERSIONS_API_V1, **PATH_TO_DATA_MODEL_VERSIONS_API_V2}

ENDPOINT_PATTERNS = ("/data/{analysistype}", "/{analysistype}/")
