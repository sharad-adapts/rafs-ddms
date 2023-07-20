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

from app.models.domain.osdu.osdu_wks_AbstractCommonResources_1.field_0 import (
    Field0 as CommonResources,
)


def create_default_dataset_record(
    dataset_id: str,
    file_source: str,
    file_size: str,
    parent_record: dict,
    schema_authority: str = "osdu",
):
    common_resources = {
        key
        for key, properties in CommonResources.schema()["properties"].items()
        if properties.get("copy_to_dataset_record")
    }
    existent_common_resources = set(parent_record["data"].keys()).intersection(common_resources)
    record_data = {key: parent_record["data"][key] for key in existent_common_resources}
    record_data.update({
        "DatasetProperties": {
            "FileSourceInfo": {
                "FileSource": file_source,
                "FileSize": file_size,
            },
        },
    })
    return {
        "id": dataset_id,
        "kind": f"{schema_authority}:wks:dataset--File.Generic:1.0.0",
        "acl": parent_record["acl"],
        "legal": parent_record["legal"],
        "data": record_data,
    }
