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

from app.api.routes.utils.records import (
    DATASET_ID_INDEX,
    VERSION_SPLIT_INDEX_COLON_IN_ID,
)


class CommonHelper(object):
    """Methods to work with all test."""

    @staticmethod
    def create_data_copies(original_data, num_copies):
        """Creates data copies of data objects with generated id."""
        copies = [copy.deepcopy(original_data) for _ in range(num_copies)]
        for copy_index, copy_data in enumerate(copies):
            copy_data["id"] = f"{copy_data['id']}_Autotest_{copy_index}"
        return copies

    @staticmethod
    def get_dataset_id_from_ddms_urn(ddms_urn):
        """Gets the dataset_id part from full urn."""
        full_id = ddms_urn.split("/")[DATASET_ID_INDEX]
        return ":".join(full_id.split(":")[VERSION_SPLIT_INDEX_COLON_IN_ID])
