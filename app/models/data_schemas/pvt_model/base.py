#  Copyright 2024 ExxonMobil Technology and Engineering Company
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
from app.resources.paths import PVTModelRelativePaths

from app.models.data_schemas.pvt_model.eos_content_model import Model as EoSContentModel
from app.models.data_schemas.pvt_model.component_scenario_model import Model as ComponentScenarioModel

EOS_CONTENT_MODELS = {
    ContentSchemaVersion.V_1_0_0: EoSContentModel,
}

COMPONENT_SCENARIO_MODELS = {
    ContentSchemaVersion.V_1_0_0: ComponentScenarioModel,
}

pvt_relative_paths = PVTModelRelativePaths()
PATHS_TO_CONTENT_PVT_MODELS = {
    pvt_relative_paths.EOS: EOS_CONTENT_MODELS,
    pvt_relative_paths.COMPONENT_SCENARIO: COMPONENT_SCENARIO_MODELS,
}
