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

from abc import ABC, abstractmethod

from loguru import logger

from app.core.settings.app import AppSettings


class IBlobLoader(ABC):

    @abstractmethod
    async def upload_blob(self, upload_url: str, blob: bytes):
        raise NotImplementedError()

    @abstractmethod
    async def download_blob(self, download_url: str) -> bytes:
        raise NotImplementedError()


def get_blob_loader(settings: AppSettings) -> IBlobLoader:
    logger.info(settings.cloud_provider)
    match settings.cloud_provider:
        case "azure":
            from app.providers.dependencies.az.blob_loader import BlobLoader
            return BlobLoader()
        case _:
            raise NotImplementedError()
