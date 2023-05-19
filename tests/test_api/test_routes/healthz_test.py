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

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK

from app.main import app
from tests.test_api.api_version import API_VERSION


@pytest.mark.asyncio
async def test_healthz_request():
    async with AsyncClient(base_url="http://testserver", app=app) as client:
        response = await client.get(f"/api/os-rafs-ddms/{API_VERSION}/healthz")

    assert response.status_code == HTTP_200_OK

    assert response.json() == {"status": "healthy"}
