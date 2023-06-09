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

from app.api.routes.utils.query import divide_chunks, find_osdu_ids_from_string


def test_divide_chunks():
    elements = [1, 2, 3, 4, 5, 6, 7, 8]

    result_chunk_size_3 = list(divide_chunks(elements, 3))
    assert result_chunk_size_3 == [[1, 2, 3], [4, 5, 6], [7, 8]]

    result_chunk_size_2 = list(divide_chunks(elements, 2))
    assert result_chunk_size_2 == [[1, 2], [3, 4], [5, 6], [7, 8]]


def test_find_osdu_ids_from_string():
    master_data_ids = "partition:master-data--MDEntityA:md_entity_a: partition:master-data--MDEntityB:md_entity_b:"
    reference_data_ids = "partition:reference-data--RefEntityA:ref_entity_a: partition:master-data--RefEntityB:ref_entity_b:"
    work_product_component_ids = "[partition:work-product-component--WPCEntityA:wpc_entity_a:,partition:work-product-component--WPCEntityB:wpc_entity_b:]"

    input_string = f"This is a sample string with OSDU IDs: {master_data_ids}, {reference_data_ids}, {work_product_component_ids}."
    expected_ids = {
        "partition:master-data--MDEntityA:md_entity_a",
        "partition:master-data--MDEntityB:md_entity_b",
        "partition:reference-data--RefEntityA:ref_entity_a",
        "partition:master-data--RefEntityB:ref_entity_b",
        "partition:work-product-component--WPCEntityA:wpc_entity_a",
        "partition:work-product-component--WPCEntityB:wpc_entity_b",

    }
    result = find_osdu_ids_from_string(input_string)
    assert result == expected_ids
