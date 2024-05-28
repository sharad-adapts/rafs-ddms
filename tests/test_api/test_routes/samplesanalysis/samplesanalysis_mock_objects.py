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

import copy
import io
import json

import pandas as pd

START_TEST_INDEX = 1  # inclusive
END_TEST_INDEX = 11  # not inclusive

SAMPLES_ANALYSIS_TEMPLATE = {
    "data": {
        "DDMSDatasets": [
            "urn://rafs-v2/nmrdata/opendes:work-product-component--SamplesAnalysis:{sa_id}/opendes:dataset--File.Generic:nmr-{ds_id}:1234/1.0.0",
        ],
    },
    "kind": "osdu:wks:work-product-component--SamplesAnalysis:1.0.0",
    "id": "opendes:work-product-component--SamplesAnalysis:{sa_id}",
}


def build_search_find_records_response(start_index=START_TEST_INDEX, end_index=END_TEST_INDEX):
    sa_records = [copy.deepcopy(SAMPLES_ANALYSIS_TEMPLATE) for _ in range(start_index, end_index)]
    for ix, record in enumerate(sa_records, start=start_index):
        record["id"] = record["id"].format(sa_id=ix)
        record["data"]["DDMSDatasets"][0] = record["data"]["DDMSDatasets"][0].format(sa_id=ix, ds_id=ix)

    return {
        "results": sa_records,
    }


def build_dataset_get_signed_urls_response(start_index=START_TEST_INDEX, end_index=END_TEST_INDEX):
    return [
        ("opendes:dataset--File.Generic:nmr-{ds_id}:1234".format(ds_id=ix), "http://{n}".format(n=ix))
        for ix in range(start_index, end_index)
    ]


NMR_ORIENT_SPLIT_TEST_TEMPLATE = {
    "columns": [
        "SamplesAnalysisID",
        "SampleID",
        "NMRTest",
    ],
    "index": [
        0,
    ],
    "data": [
        [
            "opendes:work-product-component--SamplesAnalysis:{sa_id}:",
            "opendes:master-data--Sample:Sample:",
            {
                "ExampleKey": "Example-{ex_id}",
                "NumberKey": 0,
            },
        ],
    ],
}


def build_orient_split_tests(start_index=START_TEST_INDEX, end_index=END_TEST_INDEX):
    orient_split_tests = [copy.deepcopy(NMR_ORIENT_SPLIT_TEST_TEMPLATE) for _ in range(start_index, end_index)]

    for ix, record in enumerate(orient_split_tests, start=start_index):
        record["data"][0][0] = record["data"][0][0].format(sa_id=ix)
        record["data"][0][2]["ExampleKey"] = record["data"][0][2]["ExampleKey"].format(ex_id=ix)
        record["data"][0][2]["NumberKey"] = ix

    return orient_split_tests


def build_parquet_loader_read_parquets_response(start_index=START_TEST_INDEX, end_index=END_TEST_INDEX, with_error=None):
    orient_split_tests = build_orient_split_tests(start_index, end_index)

    dataframes = [pd.read_json(io.StringIO(json.dumps(test)), orient="split") for test in orient_split_tests]

    return [
        ("opendes:dataset--File.Generic:nmr-{ds_id}".format(ds_id=ix), dataframes[ix - 1], with_error)
        for ix in range(start_index, end_index)
    ]


def build_sa_ids_response(start_index=START_TEST_INDEX, end_index=END_TEST_INDEX):
    return [
        "opendes:work-product-component--SamplesAnalysis:{sa_id}".format(sa_id=ix)
        for ix in range(start_index, end_index)
    ]


def get_aggregated_count(count):
    return {
        "result": {
            "columns": [
                "SamplesAnalysisID",
            ],
            "index": [
                "count",
            ],
            "data": [
                [
                    count,
                ],
            ],
        },
        "offset": 0,
        "page_limit": 100,
        "total_size": count,
    }
