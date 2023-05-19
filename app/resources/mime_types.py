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

# Copyright 2021 Schlumberger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Generator, List, NamedTuple


class MimeType(NamedTuple):
    """Expected always lower case."""

    type: str
    extension: str
    alternative_types: List[str] = []

    def match(self, str_value: str) -> bool:
        if not str_value:
            return False
        normalized_value = str_value.lower()
        return any(
            normalized_value == a_type
            for a_type in [self.type] + self.alternative_types
        ) or normalized_value.replace(
            ".",
            "",
        ) == self.extension.replace(".", "")


class CustomMimeTypes:
    """
    define mime types used in the application
    Note: May be use https://docs.python.org/3/library/mimetypes.html
    mimetypes.add_type('application/x-parquet', '.parquet')
    """

    PARQUET = MimeType(
        type="application/x-parquet",
        extension=".parquet",
        alternative_types=["application/parquet"],
    )  # because https://tools.ietf.org/html/rfc6838#section-3.4

    FEATHER = MimeType(
        type="application/x-feather",
        extension=".feather",
        alternative_types=["application/feather"],
    )

    JSON = MimeType(type="application/json", extension=".json")

    MSGPACK = MimeType(
        type="application/x-msgpack",
        extension=".msgpack",
        alternative_types=[
            "application/msgpack",
            "application/messagepack",
            "application/x-messagepack",
            "application/vnd.messagepack",
            "application/vnd.msgpack",
        ],
    )

    ZIP = MimeType(
        type="application/zip",
        extension=".zip",
        alternative_types=[
            "application/x-zip-compressed",
            "multipart/x-zip",
            "application/zip-compressed",
        ],
    )

    BIN = MimeType(
        type="application/octet-stream",
        extension=".bin",
        alternative_types=[],
    )

    XLXS = MimeType(
        type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        extension=".xlsx",
        alternative_types=[],
    )

    @classmethod
    def types(cls) -> Generator[MimeType, None, None]:
        """Enumerate all type."""
        for _, mime_type in cls.__dict__.items():
            if isinstance(mime_type, MimeType):
                yield mime_type

    @classmethod
    def from_str(cls, content_type: str) -> MimeType:
        for mime_type in cls.types():
            if mime_type.match(content_type):
                return mime_type
        raise ValueError(f"{content_type} does not match any supported mime types")

    # TODO add guess_type(path_like) method ?
