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

from app.models.data_schemas.pvt_model.eos_peng_robinson_lohrenz import Model as EOSPengRobinsonLohrenzModel

EOS_PENG_ROBINSON_LOHRENZ_MODELS = {
    ContentSchemaVersion.V_1_0_0: EOSPengRobinsonLohrenzModel,
}

pvt_relative_paths = PVTModelRelativePaths()
PATHS_TO_CONTENT_PVT_MODELS = {
    pvt_relative_paths.EOS_PENG_ROBINSON_LOHRENZ: EOS_PENG_ROBINSON_LOHRENZ_MODELS
}
