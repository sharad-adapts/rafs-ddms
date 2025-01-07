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

from app.models.data_schemas.version import ContentSchemaVersion
from app.resources.paths import CommonRelativePathsV2
from app.models.data_schemas.api_v2.rca_data_model_1_0_0 import RcaModel100
from app.models.data_schemas.api_v2.cce_data_model_1_0_0 import CceModel100
from app.models.data_schemas.api_v2.diff_lib_data_model import DiffLibDataSchema as DiffLibModel
from app.models.data_schemas.api_v2.transport_test_data_model_1_0_0 import TransportTestModel100
from app.models.data_schemas.api_v2.atmospheric_flash_and_compositional_analysis_data_model_1_0_0 import AtmosphericFlashAndCompositionalAnalysisModel100
from app.models.data_schemas.api_v2.mss_data_model import MssDataSchema as MSSModel
from app.models.data_schemas.api_v2.swelling_test_data_model_1_0_0 import SwellingTestModel100
from app.models.data_schemas.api_v2.cvd_data_model_1_0_0 import CvdModel100
from app.models.data_schemas.api_v2.water_analysis_data_model import WaterAnalysisDataSchema as WaterAnalysisModel
from app.models.data_schemas.api_v2.interfacial_tension_data_model import InterfacialTensionDataSchema as InterfacialTensionModel
from app.models.data_schemas.api_v2.vle_data_model import VleDataSchema as VLEModel
from app.models.data_schemas.api_v2.mcm_data_model import McmDataSchema as MCMModel
from app.models.data_schemas.api_v2.slimtube_data_model import SlimtubeDataSchema as SlimtubeModel
from app.models.data_schemas.api_v2.extraction_data_model import ExtractionDataSchema as ExtractionModel
from app.models.data_schemas.api_v2.fractionation_data_model import FractionationDataSchema as FractionationModel
from app.models.data_schemas.api_v2.relative_permeability_data_model_1_0_0 import RelativePermeabilityModel100
from app.models.data_schemas.api_v2.rock_compressibility_data_model import RockCompressibilityDataSchema as RockCompressibilityModel
from app.models.data_schemas.api_v2.electrical_properties_data_model_1_0_0 import ElectricalPropertiesModel100
from app.models.data_schemas.api_v2.nmr_data_model import NmrDataSchema as NMRModel
from app.models.data_schemas.api_v2.multiple_salinity_data_model import MultipleSalinityDataSchema as MultipleSalinityModel
from app.models.data_schemas.api_v2.gcms_alkanes_data_model import GcmsAlkanesDataSchema as GCMSAlkanesModel
from app.models.data_schemas.api_v2.gcms_aromatics_data_model import GcmsAromaticsDataSchema as GCMSAromaticsModel
from app.models.data_schemas.api_v2.gcms_ratios_data_model import GcmsRatiosDataSchema as GCMSRatiosModel
from app.models.data_schemas.api_v2.gas_chromatography_data_model_1_0_0 import GasChromatographyModel100 as GasChromatographyModel
from app.models.data_schemas.api_v2.gas_composition_data_model_1_0_0 import GasCompositionModel100
from app.models.data_schemas.api_v2.gas_chromatography_data_model_1_0_0 import GasChromatographyModel100
from app.models.data_schemas.api_v2.gas_composition_data_model import GasCompositionDataSchema as GasCompositionModel
from app.models.data_schemas.api_v2.isotope_analysis_data_model import IsotopeAnalysisDataSchema as IsotopeAnalysisModel
from app.models.data_schemas.api_v2.bulk_pyrolysis_data_model import BulkPyrolysisDataSchema as BulkPyrolysisModel
from app.models.data_schemas.api_v2.core_gamma_data_model import CoreGammaDataSchema as CoreGammaModel
from app.models.data_schemas.api_v2.uniaxial_test_data_model import UniaxialTestDataSchema as UniaxialTestModel
from app.models.data_schemas.api_v2.gcmsms_data_model import GcmsmsDataSchema as GCMSMS_Model
from app.models.data_schemas.api_v2.cec_data_model import CecDataSchema as CECContentModel
from app.models.data_schemas.api_v2.triaxial_test_data_model import TriaxialTestDataSchema as TriaxialTestModel
from app.models.data_schemas.api_v2.wettability_index_data_model import WettabilityIndexDataSchema as WettabilityIndexModel
from app.models.data_schemas.api_v2.tec_data_model import TecDataSchema as TECModel
from app.models.data_schemas.api_v2.eds_mapping_data_model import EdsMappingDataSchema as EDSMappingModel
from app.models.data_schemas.api_v2.xrf_data_model import XrfDataSchema as XRFModel
from app.models.data_schemas.api_v2.capillary_pressure_data_model_1_0_0 import CapillaryPressureModel100
from app.models.data_schemas.api_v2.sto_data_model_1_0_0 import StoModel100
from app.models.data_schemas.api_v2.tensile_strength_data_model import TensileStrengthDataSchema as TensileStrengthModel
from app.models.data_schemas.api_v2.vitrinite_reflectance_data_model import VitriniteReflectanceDataSchema as VitriniteReflectanceModel
from app.models.data_schemas.api_v2.xrd_data_model import XrdDataSchema as XRDModel
from app.models.data_schemas.api_v2.pdp_data_model import PdpDataSchema as PdpModel
from app.models.data_schemas.api_v2.crushed_rock_analysis_data_model import CrushedRockAnalysisDataSchema as CrushedRockAnalysisModel
from app.models.data_schemas.api_v2.mining_geotech_logging_data_model import MiningGeotechLoggingDataSchema as MiningGeotechLoggingModel

RCA_MODELS = {
    ContentSchemaVersion.V_1_0_0: RcaModel100,
}
CCE_MODELS = {
    ContentSchemaVersion.V_1_0_0: CceModel100,
}
DIFF_LIB_MODELS = {
    ContentSchemaVersion.V_1_0_0: DiffLibModel,
}
TRANSPORT_TEST_MODELS = {
    ContentSchemaVersion.V_1_0_0: TransportTestModel100,
}
COMPOSITIONAL_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: AtmosphericFlashAndCompositionalAnalysisModel100,
}
ATMOSPHERIC_FLASH_MODELS = {
    ContentSchemaVersion.V_1_0_0: AtmosphericFlashAndCompositionalAnalysisModel100,
}
MSS_MODELS = {
    ContentSchemaVersion.V_1_0_0: MSSModel,
}
SWELLING_MODELS = {
    ContentSchemaVersion.V_1_0_0: SwellingTestModel100,
}
CVD_MODELS = {
    ContentSchemaVersion.V_1_0_0: CvdModel100,
}
WATER_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: WaterAnalysisModel,
}
INTERFACIAL_TENSION_MODELS = {
    ContentSchemaVersion.V_1_0_0: InterfacialTensionModel,
}
VLE_MODELS = {
    ContentSchemaVersion.V_1_0_0: VLEModel,
}
MCM_MODELS = {
    ContentSchemaVersion.V_1_0_0: MCMModel,
}
SLIMTUBE_MODELS = {
    ContentSchemaVersion.V_1_0_0: SlimtubeModel,
}
EXTRACTION_MODELS = {
    ContentSchemaVersion.V_1_0_0: ExtractionModel,
}
FRACTIONATION_MODELS = {
    ContentSchemaVersion.V_1_0_0: FractionationModel,
}
RELATIVE_PERMEABILITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: RelativePermeabilityModel100,
}
ROCK_COMPRESSIBILITY_MODELS = {
    ContentSchemaVersion.V_1_0_0: RockCompressibilityModel,
}
ELECTRICAL_PROPERTIES_MODELS = {
    ContentSchemaVersion.V_1_0_0: ElectricalPropertiesModel100,
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
GCMS_AROMATICS_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSAromaticsModel,
}
GCMS_RATIOS_MODELS = {
    ContentSchemaVersion.V_1_0_0: GCMSRatiosModel,
}
GAS_CHROMATOGRAPHY_MODELS = {
    ContentSchemaVersion.V_1_0_0: GasChromatographyModel100,
}
GAS_COMPOSITION_MODELS = {
    ContentSchemaVersion.V_1_0_0: GasCompositionModel100,
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
CAP_PRESSURE_MODELS = {
    ContentSchemaVersion.V_1_0_0: CapillaryPressureModel100
}
WETTABILITY_INDEX_MODELS = {
    ContentSchemaVersion.V_1_0_0: WettabilityIndexModel
}
TEC_MODELS = {
    ContentSchemaVersion.V_1_0_0: TECModel
}
EDS_MAPPING_MODELS = {
    ContentSchemaVersion.V_1_0_0: EDSMappingModel
}
XRF_MODELS = {
    ContentSchemaVersion.V_1_0_0: XRFModel
}
TENSILE_STRENGTH_MODELS = {
    ContentSchemaVersion.V_1_0_0: TensileStrengthModel
}
VITRINITE_REFLECTANCE_MODELS = {
    ContentSchemaVersion.V_1_0_0: VitriniteReflectanceModel,
}
XRD_MODELS = {
    ContentSchemaVersion.V_1_0_0: XRDModel,
}
PDP_MODELS = {
    ContentSchemaVersion.V_1_0_0: PdpModel,
}
STO_MODELS = {
    ContentSchemaVersion.V_1_0_0: StoModel100,
}
CRUSHED_ROCK_ANALYSIS_MODELS = {
    ContentSchemaVersion.V_1_0_0: CrushedRockAnalysisModel,
}
MINING_GEOTECH_LOGGING_MODELS = {
    ContentSchemaVersion.V_1_0_0: MiningGeotechLoggingModel,
}

common_relative_paths_api_v2 = CommonRelativePathsV2()
PATH_TO_DATA_MODEL_VERSIONS_API_V2 = {
    common_relative_paths_api_v2.ROUTINECOREANALYSIS: RCA_MODELS,
    common_relative_paths_api_v2.CCE: CCE_MODELS,
    common_relative_paths_api_v2.DIFF_LIB: DIFF_LIB_MODELS,
    common_relative_paths_api_v2.TRANSPORT_TEST: TRANSPORT_TEST_MODELS,
    common_relative_paths_api_v2.COMPOSITIONAL_ANALYSIS: COMPOSITIONAL_ANALYSIS_MODELS,
    common_relative_paths_api_v2.ATMOSPHERIC_FLASH: ATMOSPHERIC_FLASH_MODELS,
    common_relative_paths_api_v2.MSS: MSS_MODELS,
    common_relative_paths_api_v2.SWELLING: SWELLING_MODELS,
    common_relative_paths_api_v2.CVD: CVD_MODELS,
    common_relative_paths_api_v2.WATER_ANALYSIS: WATER_ANALYSIS_MODELS,
    common_relative_paths_api_v2.INTERFACIAL_TENSION: INTERFACIAL_TENSION_MODELS,
    common_relative_paths_api_v2.VLE: VLE_MODELS,
    common_relative_paths_api_v2.MCM: MCM_MODELS,
    common_relative_paths_api_v2.SLIMTUBE: SLIMTUBE_MODELS,
    common_relative_paths_api_v2.EXTRACTION: EXTRACTION_MODELS,
    common_relative_paths_api_v2.FRACTIONATION: FRACTIONATION_MODELS,
    common_relative_paths_api_v2.RELATIVE_PERMEABILITY: RELATIVE_PERMEABILITY_MODELS,
    common_relative_paths_api_v2.ROCK_COMPRESSIBILITY: ROCK_COMPRESSIBILITY_MODELS,
    common_relative_paths_api_v2.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS,
    common_relative_paths_api_v2.NMR: NMR_MODELS,
    common_relative_paths_api_v2.MULTIPLE_SALINITY: MULTIPLE_SALINITY_MODELS,
    common_relative_paths_api_v2.GCMS_ALKANES: GCMS_ALKANES_MODELS,
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
    common_relative_paths_api_v2.CAP_PRESSURE: CAP_PRESSURE_MODELS,
    common_relative_paths_api_v2.WETTABILITY_INDEX: WETTABILITY_INDEX_MODELS,
    common_relative_paths_api_v2.TEC: TEC_MODELS,
    common_relative_paths_api_v2.EDS_MAPPING: EDS_MAPPING_MODELS,
    common_relative_paths_api_v2.XRF: XRF_MODELS,
    common_relative_paths_api_v2.TENSILE_STRENGTH: TENSILE_STRENGTH_MODELS,
    common_relative_paths_api_v2.VITRINITE_REFLECTANCE: VITRINITE_REFLECTANCE_MODELS,
    common_relative_paths_api_v2.XRD: XRD_MODELS,
    common_relative_paths_api_v2.PDP: PDP_MODELS,
    common_relative_paths_api_v2.STO: STO_MODELS,
    common_relative_paths_api_v2.CRUSHED_ROCK_ANALYSIS: CRUSHED_ROCK_ANALYSIS_MODELS,
    common_relative_paths_api_v2.MINING_GEOTECH_LOGGING: MINING_GEOTECH_LOGGING_MODELS,
}
