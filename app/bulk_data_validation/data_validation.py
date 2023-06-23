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

from dataclasses import dataclass

import pandas as pd
import pandera as pa
from loguru import logger

from app.api.routes.utils.query import divide_chunks, find_osdu_ids_from_string
from app.core.config import get_app_settings
from app.services.storage import StorageService

settings = get_app_settings()


@dataclass
class DataValidator:
    data_schema: pa.DataFrameSchema
    storage_service: StorageService

    async def validate(self, df: pd.DataFrame) -> dict:
        """Validate dataframe.

        :param df: dataframe
        :type df: pd.DataFrame
        :return: errors or empty dict
        :rtype: dict
        """
        schema_errors = self._validate_schema(df)
        if schema_errors:
            return schema_errors

        data_integrity_errors = await self._validate_integrity(df)
        if data_integrity_errors:
            return {
                "missing_records": list(data_integrity_errors),
            }

        return {}

    def _validate_schema(self, df: pd.DataFrame) -> dict:
        """Validate dataframe using validator schema.

        :param df: dataframe
        :type df: pd.DataFrame
        :return: errors or empty dict
        :rtype: dict
        """
        errors = {}

        try:
            self.data_schema.validate(df, lazy=True)
        except pa.errors.SchemaErrors as err:
            for case in list(err.failure_cases.iloc(0)):
                check = case["check"]
                if check not in {"column_in_dataframe", "column_in_schema"}:
                    check = "invalid_type" if "dtype" in check else "invalid_value"

                column = case["column"]
                failure_case = str(case["failure_case"])
                # If the check type is "column_in_dataframe" or "column_in_schema" the column name is in
                # "failure_case" field, otherwise it is in "column" and "failure_case" contains the field value
                if column:
                    failure_desc = {column: failure_case}
                else:
                    failure_desc = failure_case

                if check not in errors.keys():
                    errors.update({check: [failure_desc]})
                else:
                    errors[check].append(failure_desc)

        return errors

    async def _find_missing_records(self, ids_to_check: list) -> set:
        """From a list of ids find if there is any record missing in storage.

        :param ids_to_check: list of ids to check
        :type ids_to_check: list
        :return: returns the set of missing (invalid) record ids
        :rtype: set
        """
        logger.debug(f"The list of ids to check exist on storage: {ids_to_check}")
        storage_response = await self.storage_service.query_records(ids_to_check)
        return set(storage_response["invalidRecords"])

    async def _validate_integrity(self, df: pd.DataFrame) -> set:
        """Validate data referential integrity.

        :param df: dataframe
        :type df: pd.DataFrame
        :return: missing records
        :rtype: list
        """
        df_string = df.to_string()
        ids_to_check = find_osdu_ids_from_string(df_string)

        missing_records = set()
        for ids_to_check_batch in divide_chunks(list(ids_to_check), settings.storage_query_limit):
            missing_records.update(await self._find_missing_records(ids_to_check=ids_to_check_batch))

        # @TODO remove once Sample and/or FluidSample master-data schema is created
        invalid_records = set()
        skip_records = ["master-data--FluidSample", "master-data--Sample"]
        for record in missing_records:
            for skip_record in skip_records:
                if skip_record in record:
                    invalid_records.add(record)

        return missing_records - invalid_records
