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

from typing import List, NamedTuple, Optional, Tuple

from loguru import logger

from app.exceptions.exceptions import UnprocessableContentException


class RecordKeys(NamedTuple):
    MIMETYPE_ID = "EncodingFormatTypeID"
    FILE_NAME = "Name"
    FILE_SOURCE_INFO = "FileSourceInfo"
    DATASET_PROPERTIES = "DatasetProperties"
    RESOURCE_ID = "ResourceID"


ID_PART_INDEX = 2
ENTITY_TYPE_INDEX = 2
VERSION_SPLIT_INDEX = 3
VERSION_SPLIT_INDEX_COLON_IN_ID = -1
DATASET_ID_INDEX = -1
FULLID_ID_INDEX = 0
FULLID_VERSION_INDEX = 1


def get_id_part(full_record_id: str) -> str:
    """Get id part from record id.

    :param full_record_id: full record id
    :type full_record_id: str
    :return: id part
    :rtype: str
    """
    id_parts = full_record_id.split(":")
    return id_parts[ID_PART_INDEX]


def get_id_version(full_record_id: str) -> Tuple[str, Optional[int]]:
    """Separately get id and version part from record id.

    :param full_record_id: full record id
    :type full_record_id: str
    :return: tuple of id and version
    :rtype: Tuple[str, Optional[str]]
    """
    splitted_id = full_record_id.split(":")
    if len(splitted_id) > VERSION_SPLIT_INDEX:  # this means that there is a ":" in id
        record_id, version = (
            ":".join(splitted_id[:VERSION_SPLIT_INDEX_COLON_IN_ID]),
            ":".join(splitted_id[VERSION_SPLIT_INDEX_COLON_IN_ID:]),
        )  # noqa: WPS221
    else:
        record_id, version = (
            ":".join(splitted_id[:VERSION_SPLIT_INDEX]),
            ":".join(splitted_id[VERSION_SPLIT_INDEX:]),
        )  # noqa: WPS221
    try:
        if version:
            version = int(version)
        else:
            version = None
    except ValueError:
        raise UnprocessableContentException(detail=f"Record id version '{version}' should be numeric")

    return record_id, version


def find_dataset_id(ddms_datasets: List[str], prefix: str) -> Optional[str]:
    """Find dataset id.

    :param ddms_datasets: ddms datasets
    :type ddms_datasets: List[str]
    :param prefix: prefix
    :type prefix: str
    :return: dataset id
    :rtype: Optional[str]
    """
    for ddms_dataset in ddms_datasets:
        dataset_id = ddms_dataset.split("/")[DATASET_ID_INDEX]
        try:
            if dataset_id and dataset_id.split(":")[ENTITY_TYPE_INDEX].startswith(prefix):  # noqa: WPS221
                return ":".join(dataset_id.split(":")[:VERSION_SPLIT_INDEX])  # noqa: WPS221
        except IndexError:
            logger.error(f"The dataset id {dataset_id} is invalid")


def update_dataset_id(ddms_datasets: List[str], ddms_urn: str, prefix: str) -> List[str]:
    """Update dataset id.

    :param ddms_datasets: ddms datasets
    :type ddms_datasets: List[str]
    :param ddms_urn: ddms urn
    :type ddms_urn: str
    :param prefix: prefix
    :type prefix: str
    :return: updated ddms datasets
    :rtype: List[str]
    """
    for index, ddms_dataset in enumerate(ddms_datasets):
        dataset_id = ddms_dataset.split("/")[DATASET_ID_INDEX]
        if dataset_id and dataset_id.split(":")[ENTITY_TYPE_INDEX].startswith(prefix):  # noqa: WPS221
            ddms_datasets[index] = ddms_urn
            return ddms_datasets


def generate_dataset_urn(ddms_id: str, api_version: str, entity_type: str, wpc_id: str, dataset_id: str) -> str:
    """Generate dataset urn.

    :param ddms_id: ddms is
    :type ddms_id: str
    :param api_version: api version
    :type api_version: str
    :param entity_type: entity type
    :type entity_type: str
    :param wpc_id: wpc id
    :type wpc_id: str
    :param dataset_id: dataset id
    :type dataset_id: str
    :return: dataset urn
    :rtype: str
    """
    return f"urn://{ddms_id}-{api_version}/{entity_type}/{wpc_id}/{dataset_id}"


def dataset_id_exist(ddms_datasets: List[str], dataset_id: str) -> bool:
    """Checks if given dataset id exist in ddms_datasets list.

    :param ddms_datasets: ddms datasets list
    :type ddms_datasets: List[str]
    :param dataset_id: dataset id
    :type dataset_id: str
    :return: True if dataset exist in list
    :rtype: bool
    """
    for ddms_dataset in ddms_datasets:
        full_dataset_id = ddms_dataset.split("/")[DATASET_ID_INDEX]
        ddms_dataset_id, _ = get_id_version(full_dataset_id)
        if dataset_id == ddms_dataset_id:
            return True
    return False
