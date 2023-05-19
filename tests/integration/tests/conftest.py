#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
import copy
import logging
import time

import pytest
from starlette import status

from tests.integration.config import PVT_FILE
from tests.integration.tests.test_pvt import ID_PVT_TEMPLATE


@pytest.fixture(scope="module")
def create_pvt(api, tests_data):
    """Fixture to create a pvt record with a random unique id."""
    tests_data = tests_data(PVT_FILE)
    json_obj_copy = copy.deepcopy(tests_data)
    json_obj_copy["id"] = f"{ID_PVT_TEMPLATE}{int(time.time())}"
    api.pvt.post_pvt_data([json_obj_copy])

    yield json_obj_copy

    logging.info(f"Deleting a PVT record with ID {json_obj_copy['id']}")
    api.pvt.soft_delete_record(json_obj_copy["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
