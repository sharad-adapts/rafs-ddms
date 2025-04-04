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

# generated by datamodel-codegen:
#   filename:  /api/schema-service/v1/schema/osdu:wks:master-data--Sample:1.0.0
#   timestamp: 2023-10-24T20:27:08+00:00

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Extra, Field, constr


class Field0(BaseModel):
    class Config:
        extra = Extra.forbid

    viewers: List[
        constr(
            regex=r"^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$"
        )
    ] = Field(
        ...,
        description="The list of viewers to which this data record is accessible/visible/discoverable formatted as an email (core.common.model.storage.validation.ValidationDoc.EMAIL_REGEX).",
        title="List of Viewers",
    )
    owners: List[
        constr(
            regex=r"^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$"
        )
    ] = Field(
        ...,
        description="The list of owners of this data record formatted as an email (core.common.model.storage.validation.ValidationDoc.EMAIL_REGEX).",
        title="List of Owners",
    )
