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

import json
from typing import Any

from fastapi import Response
from fastapi_cache.coder import Coder, JsonCoder, PickleCoder

from app.resources.mime_types import SupportedMimeTypes


class ResponseCoder(Coder):
    @classmethod
    def encode(cls, response: Response) -> str:
        """Encode to keep value in storage."""
        media_type = response.media_type
        if media_type == SupportedMimeTypes.JSON.mime_type:
            coder = JsonCoder
        else:
            coder = PickleCoder
        encoded_content = coder.encode(response.body)
        return json.dumps({
            "encoded_content": encoded_content,
            "media_type": media_type,
        })

    @classmethod
    def decode(cls, value_to_decode: str) -> Any:
        """Decode value returned from storage."""
        value_to_decode = json.loads(value_to_decode)
        media_type = value_to_decode.get("media_type")
        encoded_content = value_to_decode.get("encoded_content")
        if media_type == SupportedMimeTypes.JSON.mime_type:
            coder = JsonCoder
        else:
            coder = PickleCoder
        return Response(
            content=coder.decode(encoded_content),
            media_type=media_type,
        )
