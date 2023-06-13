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
from typing import Iterable, List, Optional, TypeVar

from fastapi import Depends, HTTPException, Query, Request
from loguru import logger
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from starlette import status

from app.api.dependencies.services import get_async_search_service
from app.api.routes.utils.records import get_id_version
from app.exceptions.exceptions import (
    InvalidDatasetException,
    RecordValidationException,
)
from app.models.domain.osdu.base import (
    CCE_KIND,
    COMPOSITIONAL_ANALYSIS_KIND,
    CORING_KIND,
    CVD_KIND,
    DIF_LIB_KIND,
    IMPLEMENTED_MODELS,
    INTERFACIAL_TENSION_KIND,
    MCM_KIND,
    MSS_KIND,
    PATH_TO_DATA_MODEL,
    PVT_KIND,
    ROCKSAMPLE_KIND,
    ROCKSAMPLEANALYSIS_KIND,
    SLIMTUBETEST_KIND,
    STO_KIND,
    SWELLING_KIND,
    TRANSPORT_TEST_KIND,
    VLE_KIND,
    WATER_ANALYSYS_KIND,
)
from app.models.schemas.osdu_storage import OsduStorageRecord
from app.models.schemas.pandas_dataframe import OrientSplit
from app.resources.filters import SQLFilterValidator
from app.resources.paths import CommonRelativePaths
from app.services.search import SearchService

Model = TypeVar("Model", bound=BaseModel)


async def get_all_ids_from_records(
    records: List[dict],
    fields: List[str],
) -> List[str]:
    """Get the list of all ids in the records fields.

    :param List[dict] records: list of records
    :param List[str] fields: list of fields to collect
    :return: list of ids
    """
    ids_list = []

    def get_id(id_data):
        """Generator to get record ids from different record data field
        values."""
        if isinstance(id_data, str):
            yield id_data
        elif isinstance(id_data, Iterable):
            if isinstance(id_data, dict):
                for id_value in id_data.values():
                    yield from get_id(id_value)
            else:
                yield from id_data

    for record in records:
        for field in fields:
            field_data = record["data"].get(field, None)
            ids_list.extend(list(get_id(field_data)))

    return ids_list


async def validate_referential_integrity(
    records: List[dict],
    fields: List[str],
    search_service: SearchService,
):
    """Performs referential integrity validation.

    :param List[dict] records: list of records to validate
    :param List[str] fields: list of fields to validate
    :param SearchService search_service: the search service instance
    :raises HTTPException: Status 422 if any of the references is not found.
    """
    all_test_ids = await get_all_ids_from_records(records, fields)

    all_test_ids = {get_id_version(test_id)[0] for test_id in all_test_ids}

    search_response = {}
    if all_test_ids:
        query = 'id: "{ids}"'.format(ids='" OR id: "'.join(all_test_ids))
        search_response = await search_service.find_records(query=query, limit=len(all_test_ids))

    ids_found = {record_found["id"] for record_found in search_response.get("results", [])}

    missing_ids = all_test_ids.difference(ids_found)
    if missing_ids:
        reason = f"Records not found: {missing_ids}"
        logger.debug(reason)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=reason,
        )


def validate_record(record: dict, kind: str):
    """Validates given record against Osdu Model.

    :param dict record: record
    :param str kind: kind
    :raises RuntimeError: if there is not an Osdu Model that matches
    :raises ValidationError: if matches Osdu Model but it's not compliant
    """
    osdu_model = IMPLEMENTED_MODELS.get(kind)  # type Model
    if not osdu_model:
        raise RuntimeError("No valid entity in kind found or not implemented.")
    osdu_model.parse_obj(record)


async def validate_records_payload(records_list: List[OsduStorageRecord], kind: str) -> List[dict]:
    """Validates request payload.

    :param List[OsduStorageRecord] records_list: records_list
    :param str kind: records' kind
    :raises HTTPException: raises 422 if exceptions are found
    :return List[dict]: returns the list of validated records
    """
    validated = []
    skipped = []
    for record in records_list:
        record_dict = record.dict(exclude_none=True)
        try:
            validate_record(record_dict, kind)
        except RuntimeError as rexc:
            skipped.append({"id": record_dict.get("id"), "reason": rexc})
        except ValidationError as vexc:
            skipped.append({"id": record_dict.get("id"), "reason": vexc})
        validated.append(record_dict)

    if skipped:
        reason = f"Validation failed for {kind}. Skipped records {skipped}"
        logger.debug(reason)
        raise RecordValidationException(detail=reason)

    logger.debug(f"Records successfully validated for {kind}")
    return validated


async def validate_coring_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, CORING_KIND)


async def validate_rocksample_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, ROCKSAMPLE_KIND)


async def validate_rocksampleanalysis_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, ROCKSAMPLEANALYSIS_KIND)


async def validate_pvt_records_payload(
    records_list: List[OsduStorageRecord],
    search_service: SearchService = Depends(get_async_search_service),
):
    records = await validate_records_payload(records_list, PVT_KIND)
    await validate_referential_integrity(records, ["PVTTests"], search_service)
    return records


async def validate_cce_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, CCE_KIND)


async def validate_dif_lib_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, DIF_LIB_KIND)


async def validate_transport_test_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, TRANSPORT_TEST_KIND)


async def validate_com_analysis_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, COMPOSITIONAL_ANALYSIS_KIND)


async def validate_mss_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, MSS_KIND)


async def validate_swelling_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, SWELLING_KIND)


async def validate_cvd_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, CVD_KIND)


async def validate_wateranalysis_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, WATER_ANALYSYS_KIND)


async def validate_sto_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, STO_KIND)


async def validate_interfacialtension_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, INTERFACIAL_TENSION_KIND)


async def validate_vle_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, VLE_KIND)


async def validate_mcm_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, MCM_KIND)


async def validate_slimtubetest_records_payload(records_list: List[OsduStorageRecord]):
    return await validate_records_payload(records_list, SLIMTUBETEST_KIND)


async def get_data_model(request: Request) -> Model:
    """Get the model based on the request path.

    :param request: request object
    :type request: Request
    :return: The corresponding data model
    :rtype: Model
    """
    model = None
    common_relative_paths = (
        CommonRelativePaths.CCE,
        CommonRelativePaths.ROCKSAMPLEANALYSIS,
        CommonRelativePaths.DIF_LIB,
        CommonRelativePaths.TRANSPORT_TEST,
        CommonRelativePaths.MSS,
        CommonRelativePaths.COMPOSITIONAL_ANALYSIS,
        CommonRelativePaths.SWELLING,
        CommonRelativePaths.CVD,
        CommonRelativePaths.STO_ANALYSIS,
        CommonRelativePaths.INTERFACIAL_TENSION,
        CommonRelativePaths.WATER_ANALYSIS,
        CommonRelativePaths.VLE,
        CommonRelativePaths.MCM,
        CommonRelativePaths.SLIMTUBETEST,
    )
    for path in common_relative_paths:
        if path in str(request.url.path):
            model = PATH_TO_DATA_MODEL.get(path)
            break

    if not model:
        reason = "Unimplemented model."
        logger.debug(reason)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=reason)

    return model


async def validate_filters(
    model: BaseModel = Depends(get_data_model),
    columns_filter: Optional[str] = Query(
        default=None,
        example="PropertyX,PropertyY,PropertyZ",
    ),
    rows_filter: Optional[str] = Query(
        default=None,
        example="PropertyX[.PropertyXFieldA],gt,4000",
    ),
    columns_aggregation: Optional[str] = Query(
        default=None,
        example="PropertyX[.PropertyXFieldA],avg",
    ),
) -> SQLFilterValidator:
    """Validates query parameters used for dataframe filtering.

    :param BaseModel model: pydantic model
    :param Optional[str] columns_filter: comma separated string of columns, defaults to None
    :param Optional[str] rows_filter: comma separated predicate, defaults to None
    :param Optional[str] columns_aggregation: comma separated aggregation, defaults to None
    :return SQLFilter: filter object with validations
    """
    sql_filter = SQLFilterValidator(
        model=model,
        raw_columns_filter=columns_filter,
        raw_rows_filter=rows_filter,
        raw_columns_aggregation=columns_aggregation,
    )
    try:
        any([
            sql_filter.valid_columns_aggregation,
            sql_filter.valid_columns_filter,
            sql_filter.valid_rows_filter,
        ])
    except RuntimeError as exc:
        logger.debug(f"Query parameters are invalid: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.debug("Query parameters are valid.")
    return sql_filter


async def get_validated_bulk_data_json(request: Request) -> str:
    """Validates incoming json bulk data in orient=split format.

    :param request: the incoming request object
    :type request: Request
    :raises InvalidDatasetException: if data and index are inconsistent
    :raises ValidationError: if orientsplit frame can't be build from request body
    :return: validated json data
    :rtype: str
    """
    body = await request.body()
    bulk_data = OrientSplit.parse_obj(json.loads(body.decode("utf-8")))

    index_length = len(bulk_data.index)
    data_length = len(bulk_data.data)
    if index_length != data_length:
        detail = f"Data error: 'index' lenght: {index_length} != 'data' lenght: {data_length}"
        raise InvalidDatasetException(detail=detail)
    return bulk_data.json()
