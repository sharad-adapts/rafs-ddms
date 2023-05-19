#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import hashlib
from unittest.mock import MagicMock, patch

from app.core.helpers.cache.key_builder import key_builder_using_token


class FuncMock(MagicMock):
    __module__ = "module"
    __name__ = "name"


def test_key_builder_using_token():
    query_params_items = [("key", "value")]
    data_partition_id = "test-data-partition-id"
    token = "test-token"
    url = "https://test_url"
    content_type = "application/test-content-type"
    prefix = "prefix"

    function = FuncMock()
    request = MagicMock()
    query_params = MagicMock()
    query_params.multi_items.return_value = query_params_items
    request.query_params = query_params
    request.headers = {
        "authorization": token,
        "data-partition-id": data_partition_id,
        "content-type": content_type,
    }
    request.url = url

    func_meta = f"{function.__module__}:{function.__name__}"
    query_meta = f"{data_partition_id}:{token}:{url}:{query_params_items}:{content_type}"
    hash_key = hashlib.sha256(
        f"{func_meta}:{query_meta}".encode(),
    ).hexdigest()
    test_key = f"{prefix}::{hash_key}"

    with patch(
        "fastapi_cache.FastAPICache.get_prefix",
        return_value=prefix,
    ):
        expected_key = key_builder_using_token(
            func=function,
            request=request,
        )

    assert test_key == expected_key
