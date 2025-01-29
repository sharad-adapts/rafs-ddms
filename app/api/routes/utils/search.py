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

from typing import List, Tuple

from app.api.routes.utils.records import (
    get_info_from_blob_urn,
    get_info_from_urn,
)
from app.core.config import get_app_settings


def _verify_target_content(
    dataset_id: str,
    analysis_type: str,
    current_schema_version: str,
    target_schema_version: str,
) -> bool:
    """Verify the dataset matches the correct analysis type and target schema.

    :param dataset_id: dataset id
    :type dataset_id: str
    :param analysis_type: analysis type as per rafsddms
    :type analysis_type: str
    :param current_schema_version: current schema version
    :type current_schema_version: str
    :param target_schema_version: target schema
    :type target_schema_version: str
    :return: a boolean indicating if schema and analysis type matches
    :rtype: bool
    """

    schema_match = False
    if current_schema_version == target_schema_version:
        schema_match = True

    dataset_type_match = False
    if f":{analysis_type}-" in dataset_id:
        dataset_type_match = True

    return schema_match and dataset_type_match


def _get_valid_dataset_ids_from_ddms_datasets(
    ddms_datasets: List[str],
    analysis_type: str,
    target_schema_version: str,
) -> List[Tuple[str, str]]:
    """Build a list of tuples dataset_id, samples_analysis_id.

    :param ddms_datasets: list of ddms dataset string
    :type ddms_datasets: List[str]
    :param analysis_type: the analysis type as per rafsddms
    :type analysis_type: str
    :param target_schema_version: target schema version
    :type target_schema_version: str
    :return: a list of tuples (dataset_id, samples_analysis_id)
    :rtype: List[Tuple[str, str]]
    """
    valid_ids = []
    for urn in ddms_datasets:
        urn_info = get_info_from_urn(urn)
        if not urn_info:
            continue
        content_verified = _verify_target_content(
            dataset_id=urn_info["dataset_id"],
            analysis_type=analysis_type,
            current_schema_version=urn_info["content_schema_version"],
            target_schema_version=target_schema_version,
        )
        if content_verified:
            valid_ids.append((urn_info["dataset_id"], urn_info["samples_analysis_id"]))
    return valid_ids


def _get_valid_blob_ids_from_ddms_datasets(
    ddms_datasets: List[str],
    analysis_family: str,
    analysis_type: str,
    target_schema_version: str,
) -> List[Tuple[str, str]]:
    """Build a list of tuples blob_id, samples_analysis_id.

    :param ddms_datasets: list of ddms dataset string
    :type ddms_datasets: List[str]
    :param analysis_family: the analysis family as per rafsddms
    :type analysis_family: str
    :param analysis_type: the analysis type as per rafsddms
    :type analysis_type: str
    :param target_schema_version: target schema version
    :type target_schema_version: str
    :return: a list of tuples (dataset_id, samples_analysis_id)
    :rtype: List[Tuple[str, str]]
    """
    valid_ids = []
    for urn in ddms_datasets:
        urn_info = get_info_from_blob_urn(urn)
        if not urn_info:
            continue
        analysis_family_match = analysis_family == urn_info["analysis_family"]
        analysis_type_match = analysis_type == urn_info["analysis_type"]
        schema_version_match = urn_info["version"] == target_schema_version
        if analysis_family_match and analysis_type_match and schema_version_match:
            valid_ids.append((urn_info["blob_id"], urn_info["wpc_id"]))
    return valid_ids


def get_valid_ids_from_ddms_datasets(
    ddms_datasets: List[str],
    analysis_family: str,
    analysis_type: str,
    target_schema_version: str,
) -> List[Tuple[str, str]]:
    """Build a list of tuples content_identifier, samples_analysis_id.

    :param ddms_datasets: list of ddms dataset string
    :type ddms_datasets: List[str]
    :param analysis_family: the analysis family as per rafsddms
    :type analysis_family: str
    :param analysis_type: the analysis type as per rafsddms
    :type analysis_type: str
    :param target_schema_version: target schema version
    :type target_schema_version: str
    :return: a list of tuples (dataset_id, samples_analysis_id)
    :rtype: List[Tuple[str, str]]
    """
    if get_app_settings().use_blob_storage:
        valid_ids = _get_valid_blob_ids_from_ddms_datasets(
            ddms_datasets=ddms_datasets,
            analysis_family=analysis_family,
            analysis_type=analysis_type,
            target_schema_version=target_schema_version,
        )
    else:
        valid_ids = _get_valid_dataset_ids_from_ddms_datasets(
            ddms_datasets=ddms_datasets,
            analysis_type=analysis_type,
            target_schema_version=target_schema_version,
        )
    return valid_ids
