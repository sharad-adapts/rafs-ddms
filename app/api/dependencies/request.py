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

from fastapi import Header, HTTPException, Request
from starlette import status


async def get_data_partition_id(request: Request):
    # @TODO review is required.
    # could be replaced by require_data_partition_id
    data_partition_id = request.headers.get("data-partition-id")
    if not data_partition_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data-partition-id in headers",
        )
    return data_partition_id


def require_data_partition_id(
    data_partition_id=Header(
        title="data-partition-id",
        example="opendes",
        description="Specifies the proper data partition id",
    ),
):
    return data_partition_id
