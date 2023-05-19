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

from typing import Optional

from pydantic import BaseSettings


class AzureConfig(BaseSettings):
    service_name: str = None

    keyvault_url: str = None

    use_partition_service: str = None

    az_logger_level: str = None

    az_ai_instrumentation_key: str = None

    class Config:
        env_file = ".env"


def get_cloud_provider_config(cloud_provider: str) -> Optional[BaseSettings]:
    if cloud_provider == "azure":
        return AzureConfig()
