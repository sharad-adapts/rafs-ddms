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
import copy

import pytest
from loguru import logger
from starlette import status

from tests.integration.config import (
    TEST_DATA_STORE,
    DataFiles,
    DataTemplates,
    DataTypes,
)


@pytest.fixture(scope="session", autouse=True)
def create_pvt(api, helper, tests_data):
    """Fixture to create a pvt record with a random unique id and delete it
    after test."""
    record_data = copy.deepcopy(tests_data(DataFiles.PVT))
    record_data["id"] = f"{DataTemplates.ID_PVT}{helper.generate_random_record_id()}"
    getattr(api, DataTypes.PVT).post_record([record_data])
    TEST_DATA_STORE["pvt_record_id"] = record_data["id"]

    yield record_data

    if record_data:
        api.storage.purge_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])


@pytest.fixture
def create_record(api, helper, tests_data):
    """Fixture to create any record with a random unique id and delete it after
    test."""
    record_data = {}
    _api_path = ""
    _to_delete = bool

    def _create_record(
        api_path: DataTypes,
        file_name: str,
        id_template: str,
        datasets: list = None,
        to_delete: bool = True,
    ) -> [dict | dict]:
        """
        :param api_path: example - DataTypes.RS, DataTypes.CORING, DataTypes.RSA, DataTypes.PVT
        :param file_name: see tests/integration/config.py
        :param id_template: example - ID_RSA_TEMPLATE
        :param datasets: list of raw data files tha can be downloaded
        :param to_delete: if the record needs to be deleted
        :return: created record data
        """
        nonlocal record_data, _api_path, _to_delete
        _api_path = api_path
        _to_delete = to_delete
        record_data = copy.deepcopy(tests_data(file_name))
        record_data["id"] = f"{id_template}{helper.generate_random_record_id()}"

        if datasets:
            record_data["data"]["Datasets"] = datasets

        logger.info(f"Creating a record with ID {record_data['id']}")
        created_record = getattr(api, _api_path).post_record([record_data])
        while True:
            logger.info(f"Check until record is created and registered")
            try:
                getattr(api, _api_path).get_record(record_data["id"])
            except AssertionError:
                logger.info(f"Record {record_data['id']} hasn't been created yet")
            else:
                break
        return record_data, created_record

    yield _create_record

    if _to_delete:
        api.storage.purge_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])


@pytest.fixture
def delete_record(api, helper):
    """Fixture to delete any record with id after test."""
    container = {"record_id": [], "api_path": ""}

    yield container

    for record_id in container["record_id"]:
        api.storage.purge_record(record_id, allowed_codes=[status.HTTP_204_NO_CONTENT])
