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

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.api.routes.utils.search import get_valid_ids_from_ddms_datasets
from app.models.domain.osdu.base import SAMPLESANALYSIS_KIND
from app.resources.paths import SAMPLESANALYSIS_TYPE_MAPPING
from app.services import search


class SamplesAnalysisTypeIdsFetcher(ABC):

    @abstractmethod
    async def get_ids(
        self,
        data_partition_id: str,
        analysis_type: str,
        target_schema_version: str,
        wks_parameters: Optional[dict] = None,
    ):
        raise NotImplementedError()


class SearchServiceSamplesAnalysisTypeIdsFetcher(SamplesAnalysisTypeIdsFetcher):

    def __init__(self, search_service: search.SearchService):
        self._search_service = search_service

    async def get_ids(
        self,
        data_partition_id: str,
        analysis_type: str,
        target_schema_version: str,
        wks_parameters: Optional[dict] = None,
    ):
        """Performs a query to search service to build a list of tuples
        dataset_id, samples_analysis_id."""
        query = self._build_sampleanalysistype_query(data_partition_id, SAMPLESANALYSIS_TYPE_MAPPING[analysis_type])
        query_offset = 0

        result_records = []
        while True:
            search_response = await self._search_service.find_records(
                kind=SAMPLESANALYSIS_KIND,
                query=query,
                offset=query_offset,
                limit=search.QUERY_LIMIT,
            )
            records = search_response.get("results", [])
            if not records:
                break
            result_records.extend(records)
            query_offset += search.QUERY_LIMIT

        return self._build_result_ids(result_records, target_schema_version, analysis_type)

    def _build_sampleanalysistype_query(self, data_partition_id: str, analysis_types: List[str]) -> str:
        """Build a query to be used within search service for
        SamplesAnalysisType."""

        analysis_types = [
            f'"{data_partition_id}:reference-data--SampleAnalysisType:{analysis_type}"'
            for analysis_type in analysis_types
        ]
        analysis_types_str = " OR ".join(analysis_types)
        return f"data.SampleAnalysisTypeIDs:({analysis_types_str})"

    def _build_result_ids(  # noqa: CCR001
        self,
        result_records: list,
        target_schema_version: str,
        analysis_type: str,
    ) -> List[Tuple[str, str]]:
        """Build a list of tuples dataset_id, samples_analysis_id."""

        result_ids = []
        for record in result_records:
            if ddms_datasets := record.get("data", {}).get("DDMSDatasets"):  # noqa: WPS332
                result_ids.extend(
                    get_valid_ids_from_ddms_datasets(
                        ddms_datasets=ddms_datasets,
                        analysis_family="samplesanalysis",
                        analysis_type=analysis_type,
                        target_schema_version=target_schema_version,
                    ),
                )

        return result_ids
