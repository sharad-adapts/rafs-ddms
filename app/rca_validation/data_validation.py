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

from app.services.search import SearchService


@dataclass
class DataValidator:
    data_schema: pa.DataFrameSchema
    search_service: SearchService

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
        if data_integrity_errors.get("missing_records"):
            return data_integrity_errors

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

    async def _validate_integrity(self, df: pd.DataFrame) -> dict:
        """Validate data integrity.

        :param df: dataframe
        :type df: pd.DataFrame
        :return: missing records
        :rtype: dict
        """
        fields_with_ids = [
            "RockSampleID",
            "CoringID",
            "WellboreID",
            "SampleType",
            "SampleDepth.UnitOfMeasure",
            "NetConfiningStress.UnitOfMeasure",
            "NetOverburdenPressure.UnitOfMeasure",
            "ConfiningStress.UnitOfMeasure",
            "Permeability.UnitOfMeasure",
            "Permeability.Type",
            "Porosity.UnitOfMeasure",
            "Porosity.Type",
            "GrainDensity.UnitOfMeasure",
            "GrainDensity.Type",
            "Saturation.Method",
        ]

        df = df.reset_index()

        missing_records = set()
        records_found = set()
        ids_to_check = set()
        # Max number of IDs to check. Current limit on the amount of records in response is 1000
        limit = 1000

        async def _check_records_exist():
            query = 'id: "{ids}"'.format(ids='" OR id: "'.join(ids_to_check))

            search_response = await self.search_service.find_records(query=query, limit=limit)
            searhc_results = search_response.get("results", set())
            results_ids = {record["id"] for record in searhc_results}
            missing_ids = list(ids_to_check - set(results_ids))

            if missing_ids:
                missing_records.update(missing_ids)

            ids_to_check.clear()

        # TODO Parallel the requests
        for _, row in df.iterrows():
            if len(ids_to_check) < (limit - len(fields_with_ids)):
                # Collect ids to check existence in storage. Remove ":" in the end of id for search servcice.
                ids_to_check.update(
                    {
                        row[field][:-1] for field in fields_with_ids
                        if row.get(field) and row[field] not in missing_records & records_found
                    },
                )
            else:
                await _check_records_exist()

        if ids_to_check:
            await _check_records_exist()

        return {"missing_records": list(missing_records)}
