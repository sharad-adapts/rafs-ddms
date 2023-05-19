#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import json

import pytest
from fastapi_cache.coder import JsonCoder, PickleCoder
from starlette.responses import Response

from app.core.helpers.cache.coder import ResponseCoder
from app.resources.mime_types import CustomMimeTypes


@pytest.mark.parametrize(
    "media_type,coder", [
        (CustomMimeTypes.JSON.type, JsonCoder),
        ("application/any", PickleCoder),
    ],
)
def test_response_coder_encode(media_type, coder):
    response = Response(
        content="content",
        media_type=media_type,
    )
    encoded_content = coder.encode(response.body)
    test_result = json.dumps({
        "encoded_content": encoded_content,
        "media_type": media_type,
    })

    expected_result = ResponseCoder.encode(response)

    assert test_result == expected_result


@pytest.mark.parametrize(
    "value_to_decode,coder", [
        (
            {
                "encoded_content": '"content"',
                "media_type": CustomMimeTypes.JSON.type,
            },
            JsonCoder,
        ),
        (
            {
                "encoded_content": "gASVCwAAAAAAAABDB2NvbnRlbnSULg==\n",
                "media_type": "application/any",
            },
            PickleCoder,
        ),
    ],
)
def test_response_coder_decode(value_to_decode, coder):
    encoded_content = value_to_decode.get("encoded_content")
    media_type = value_to_decode.get("media_type")
    test_result = Response(
        content=coder.decode(encoded_content),
        media_type=media_type,
    )

    expected_result = ResponseCoder.decode(json.dumps(value_to_decode))

    assert test_result.body == expected_result.body
    assert test_result.media_type == expected_result.media_type
