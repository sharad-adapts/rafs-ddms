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
from app.models.data_schemas.rock_compressibility_data_model import Model as RockCompressibilityModel
from app.models.data_schemas.electrical_properties_data_model import Model as ElectricalPropertiesModel
from app.models.data_schemas.formation_resistivity_index_data_model import Model as FormationResistivityIndexModel
from app.models.data_schemas.nmr_data_model import Model as NMRModel
from app.models.data_schemas.multiple_salinity_data_model import Model as MultipleSalinityModel
from app.models.data_schemas.gcms_alkanes_data_model import Model as GCMSAlkanesModel
from app.models.data_schemas.mercury_injection_analysis_data_model import Model as MercuryInjectionModel
from app.models.data_schemas.gcms_aromatics_data_model import Model as GCMSAromaticsModel
from app.models.data_schemas.gcms_ratios_data_model import Model as GCMSRatiosModel
from app.models.data_schemas.whole_oil_gc_data_model import Model as WholeOilGCModel
from app.models.data_schemas.gasoline_gc_data_model import Model as GasolineGCModel
from app.models.data_schemas.gas_composition_data_model import Model as GasCompositionModel
from app.models.data_schemas.isotope_analysis_data_model import Model as IsotopeAnalysisModel
from app.models.data_schemas.bulk_pyrolysis_data_model import Model as BulkPyrolysisModel
from app.resources.paths import CommonRelativePaths

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
ELECTRICAL_PROPERTIES_MODELS = {
    ContentSchemaVersion.V_1_0_0: ElectricalPropertiesModel,
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
WHOLE_OIL_GC_MODELS = {
    ContentSchemaVersion.V_1_0_0: WholeOilGCModel,
}
GASOLINE_GC_MODELS = {
    ContentSchemaVersion.V_1_0_0: GasolineGCModel,
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

common_relative_paths = CommonRelativePaths()
PATH_TO_DATA_MODEL_VERSIONS = {
    common_relative_paths.ROUTINECOREANALYSIS: RCA_MODELS,
    common_relative_paths.CCE: CCE_MODELS,
    common_relative_paths.DIF_LIB: DIFF_LIB_MODELS,
    common_relative_paths.TRANSPORT_TEST: TRANSPORT_TEST_MODELS,
    common_relative_paths.MSS: MSS_MODELS,
    common_relative_paths.COMPOSITIONAL_ANALYSIS: COMPOSITIONAL_ANALYSIS_MODELS,
    common_relative_paths.SWELLING: SWELLING_TEST_MODELS,
    common_relative_paths.CVD: CVD_MODELS,
    common_relative_paths.WATER_ANALYSIS: WATER_ANALYSIS_MODELS,
    common_relative_paths.INTERFACIAL_TENSION: INTERFACIAL_TENSION_MODELS,
    common_relative_paths.STO_ANALYSIS: STO_ANALYSIS_MODELS,
    common_relative_paths.VLE: VLE_MODELS,
    common_relative_paths.MCM: MCM_ANALYSIS_MODELS,
    common_relative_paths.SLIMTUBETEST: SLIMTUBETEST_MODELS,
    common_relative_paths.RELATIVE_PERMEABILITY: RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths.CAP_PRESSURE: CAP_PRESSURE_MODELS,
    common_relative_paths.FRACTIONATION: FRACTIONATION_MODELS,
    common_relative_paths.EXTRACTION: EXTRACTION_MODELS,
    common_relative_paths.PHYS_CHEM: PHYS_CHEM_MODELS,
    common_relative_paths.WATER_GAS_RELATIVE_PERMEABILITY: WATER_GAS_RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths.ROCK_COMPRESSIBILITY: ROCK_COMPRESSIBILITY_MODELS,
    common_relative_paths.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS,
    common_relative_paths.FORMATION_RESISTIVITY_INDEX: FORMATION_RESISTIVITY_INDEX_MODELS,
    common_relative_paths.NMR: NMR_MODELS,
    common_relative_paths.MULTIPLE_SALINITY: MULTIPLE_SALINITY_MODELS,
    common_relative_paths.GCMS_ALKANES: GCMS_ALKANES_MODELS,
    common_relative_paths.MERCURY_INJECTION: MERCURY_INJECTION_MODELS,
    common_relative_paths.GCMS_AROMATICS: GCMS_AROMATICS_MODELS,
    common_relative_paths.GCMS_RATIOS: GCMS_RATIOS_MODELS,
    common_relative_paths.WHOLE_OIL_GC: WHOLE_OIL_GC_MODELS,
    common_relative_paths.GASOLINE_GC: GASOLINE_GC_MODELS,
    common_relative_paths.GAS_COMPOSITION: GAS_COMPOSITION_MODELS,
    common_relative_paths.ISOTOPE_ANALYSIS: ISOTOPE_ANALYSIS_MODELS,
    common_relative_paths.BULK_PYROLYSIS: BULK_PYROLYSIS_MODELS,
}
