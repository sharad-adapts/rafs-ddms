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

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_versionizer.versionizer import versionize
from httpx import HTTPStatusError
from requests.exceptions import HTTPError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.errors.data_validation_error import (
    data_validation_http_error_handler,
)
from app.api.errors.http_error import http_error_handler
from app.api.errors.invalid_body_error import invalid_body_error_handler
from app.api.errors.invalid_header_error import invalid_header_error_handler
from app.api.errors.osdu_api_error import (
    osdu_api_custom_exc_handler,
    osdu_api_http_error_handler,
    osdu_api_httpx_error_handler,
)
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.exceptions.exceptions import (
    DataValidationException,
    InvalidBodyException,
    InvalidHeaderException,
    OsduApiException,
)
from app.providers.helpers.metric import init_metric

EXCEPTIONS_AND_HANDLERS = (
    (HTTPException, http_error_handler),
    (RequestValidationError, http422_error_handler),
    (HTTPError, osdu_api_http_error_handler),
    (HTTPStatusError, osdu_api_httpx_error_handler),
    (InvalidBodyException, invalid_body_error_handler),
    (InvalidHeaderException, invalid_header_error_handler),
    (DataValidationException, data_validation_http_error_handler),
    (OsduApiException, osdu_api_custom_exc_handler),
)


def get_application() -> FastAPI:
    """Prepare FastAPI application.

    :return: application
    :rtype: FastAPI
    """
    settings = get_app_settings()

    settings.configure_logging()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_metric(application, settings)

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application, settings),
    )

    application.include_router(api_router, prefix="")

    for exception, error_handler in EXCEPTIONS_AND_HANDLERS:
        application.add_exception_handler(exception, error_handler)

    versions = versionize(  # noqa: F841
        app=application,
        default_version=(application.version.split(".")[1], application.version.split(".")[2]),
        prefix_format=f"{settings.openapi_prefix}/v{{major}}",
        docs_url="/docs",
    )

    # Handlers need to be added for all versions
    # https://github.com/DeanWay/fastapi-versioning/issues/30
    for sub_app in application.routes:
        if hasattr(sub_app.app, "add_exception_handler"):
            for exception, error_handler in EXCEPTIONS_AND_HANDLERS:  # noqa: WPS440
                sub_app.app.add_exception_handler(
                    exception, error_handler,
                )

    return application


app = get_application()
