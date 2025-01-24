#  Copyright 2024 ExxonMobil Technology and Engineering Company
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

from typing import List, Optional

from app.api.routes.utils.records import get_info_from_urn


def find_dataset_id_from_type(
    ddms_datasets: List[str],
    analysis_type: str,
    version: str,
) -> Optional[str]:
    """Find dataset id from given analysis type and version.

    :param ddms_datasets: DDMSDataset list
    :type ddms_datasets: List[str]
    :param analysis_type: analysis type
    :type analysis_type: str
    :param version: content schema version
    :type version: str
    :return: the dataset id, if found
    :rtype: Optional[str]
    """
    for ddms_dataset in ddms_datasets:
        urn_info = get_info_from_urn(ddms_dataset)
        if urn_info and analysis_type in urn_info["test_type"] and urn_info["content_schema_version"] == version:
            return urn_info["dataset_id"]
