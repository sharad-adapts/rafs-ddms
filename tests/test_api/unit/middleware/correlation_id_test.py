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

import uuid

import pytest
from fastapi import FastAPI, Response
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette import status

from app.middleware.correlation_id_middleware import CorrelationIDMiddleware
from app.resources.common_headers import CORRELATION_ID

EXISTING_CORRELATION_ID = "existing-correlation-id"
TEST_ROUTE = "/"


class MockRoute(APIRoute):
    pass


@pytest.fixture
def app():
    app = FastAPI()
    route = MockRoute(TEST_ROUTE, lambda: Response(content="Hello"))
    app.router.routes = [route]
    app.add_middleware(CorrelationIDMiddleware)
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


def test_correlation_id_middleware_with_existing_header(test_client):
    response = test_client.get(TEST_ROUTE, headers={CORRELATION_ID: EXISTING_CORRELATION_ID})
    assert response.status_code == status.HTTP_200_OK
    assert CORRELATION_ID in response.headers
    assert response.headers[CORRELATION_ID] == EXISTING_CORRELATION_ID


def test_correlation_id_middleware_without_header(test_client):
    correlation_id = f"rafs-ddms/{str(uuid.uuid4())}"
    response = test_client.get(TEST_ROUTE, headers={CORRELATION_ID: correlation_id})
    assert response.status_code == status.HTTP_200_OK
    assert CORRELATION_ID in response.headers
    assert response.headers[CORRELATION_ID] == correlation_id
