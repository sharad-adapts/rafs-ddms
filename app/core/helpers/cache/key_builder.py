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

import hashlib
from typing import Callable, Optional

from starlette.requests import Request
from starlette.responses import Response


def key_builder_using_token(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    """Key builder for authorized requests."""
    from fastapi_cache import FastAPICache

    func_meta = f"{func.__module__}:{func.__name__}"
    prefix = f"{FastAPICache.get_prefix()}:{namespace}"

    token = request.headers.get("authorization")
    data_partition_id = request.headers.get("data-partition-id")
    content_type = request.headers.get("content-type")
    url = request.url
    query_params = request.query_params.multi_items()
    query_meta = f"{data_partition_id}:{token}:{url}:{query_params}:{content_type}"

    hash_key = hashlib.sha256(
        f"{func_meta}:{query_meta}".encode(),
    ).hexdigest()

    return f"{prefix}:{hash_key}"
