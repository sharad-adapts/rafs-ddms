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

from pydantic.main import BaseModel
from starlette import status


class BadRequestResponse(BaseModel):
    code: int = status.HTTP_400_BAD_REQUEST
    reason: str


class OsduApiErrorResponse(BadRequestResponse):
    message: str


class ValidationErrorResponse(BadRequestResponse):
    code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    errors: Optional[dict]
