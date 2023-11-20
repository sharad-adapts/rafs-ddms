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
from app.models.data_schemas.api_v2.rca_data_model import Model as RCAModel
from app.models.data_schemas.api_v2.electrical_properties_data_model import Model as ElectricalPropertiesModel_API_V2
from app.models.data_schemas.api_v2.nmr_data_model import Model as NMRModel
from app.models.data_schemas.api_v2.multiple_salinity_data_model import Model as MultipleSalinityModel
from app.models.data_schemas.api_v2.gcms_alkanes_data_model import Model as GCMSAlkanesModel
from app.models.data_schemas.api_v2.mercury_injection_analysis_data_model import Model as MercuryInjectionModel
from app.models.data_schemas.api_v2.gcms_aromatics_data_model import Model as GCMSAromaticsModel
from app.models.data_schemas.api_v2.gcms_ratios_data_model import Model as GCMSRatiosModel
from app.models.data_schemas.api_v2.gas_chromatography_data_model import Model as GasChromatographyModel
from app.models.data_schemas.api_v2.gas_composition_data_model import Model as GasCompositionModel
from app.models.data_schemas.api_v2.isotope_analysis_data_model import Model as IsotopeAnalysisModel
from app.models.data_schemas.api_v2.bulk_pyrolysis_data_model import Model as BulkPyrolysisModel
from app.models.data_schemas.api_v2.core_gamma_data_model import Model as CoreGammaModel
from app.models.data_schemas.api_v2.uniaxial_test_data_model import Model as UniaxialTestModel
from app.models.data_schemas.api_v2.gcmsms_data_model import Model as GCMSMS_Model
from app.models.data_schemas.api_v2.cec_content_model import Model as CECContentModel
from app.models.data_schemas.api_v2.triaxial_test_data_model import Model as TriaxialTestModel
from app.models.data_schemas.api_v2.cap_pressure_data_model import Model as CapPressureModel

RCA_MODELS = {
    ContentSchemaVersion.V_1_0_0: RCAModel,
}
ELECTRICAL_PROPERTIES_MODELS_API_V2 = {
    ContentSchemaVersion.V_1_0_0: ElectricalPropertiesModel_API_V2,
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
CAP_PRESSURE_MODELS = {
    ContentSchemaVersion.V_1_0_0: CapPressureModel
}

common_relative_paths_api_v2 = CommonRelativePathsV2()
PATH_TO_DATA_MODEL_VERSIONS_API_V2 = {
    common_relative_paths_api_v2.ROUTINECOREANALYSIS: RCA_MODELS,
    common_relative_paths_api_v2.ELECTRICAL_PROPERTIES: ELECTRICAL_PROPERTIES_MODELS_API_V2,
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
    common_relative_paths_api_v2.CAP_PRESSURE: CAP_PRESSURE_MODELS,
}
