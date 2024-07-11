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

from app.models.data_schemas.api_v1.base import PATH_TO_DATA_MODEL_VERSIONS_API_V1
from app.models.data_schemas.api_v2.base import PATH_TO_DATA_MODEL_VERSIONS_API_V2

PATH_TO_DATA_MODEL_VERSIONS_API_DEV = PATH_TO_DATA_MODEL_VERSIONS_API_V2

PATHS_TO_DATA_MODEL = {
    "v1": PATH_TO_DATA_MODEL_VERSIONS_API_V1,
    "v2": PATH_TO_DATA_MODEL_VERSIONS_API_V2,
    "dev": PATH_TO_DATA_MODEL_VERSIONS_API_DEV,
}

ALL_PATHS_TO_DATA_MODEL = PATH_TO_DATA_MODEL_VERSIONS_API_V2

ENDPOINT_PATTERNS = ("/data/{analysistype}", "/{analysistype}/")
