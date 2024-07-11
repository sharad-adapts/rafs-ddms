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

OBJECT_ARRAY_1_4 = [
    {"number": 1.0, "text": "Text1", "inner_object": {"inner_text": "InnerText1"}},
    {"number": 2.0, "text": "Text2", "inner_object": {"inner_text": "InnerText2"}},
    {"number": 3.0, "text": "Text3", "inner_object": {"inner_text": "InnerText3"}},
    {"number": 4.0, "text": "Text4", "inner_object": {"inner_text": "InnerText4"}},
]

OBJECT_ARRAY_5_8 = [
    {"number": 5.0, "text": "Text5", "inner_object": {"inner_text": "InnerText5"}},
    {"number": 6.0, "text": "Text6", "inner_object": {"inner_text": "InnerText6"}},
    {"number": 7.0, "text": "Text7", "inner_object": {"inner_text": "InnerText7"}},
    {"number": 8.0, "text": "Text8", "inner_object": {"inner_text": "InnerText8"}},
]

OBJECT_ARRAY_9_12 = [
    {"number": 9.0, "text": "Text9", "inner_object": {"inner_text": "InnerText9"}},
    {"number": 10.0, "text": "Text10", "inner_object": {"inner_text": "InnerText10"}},
    {"number": 11.0, "text": "Text11", "inner_object": {"inner_text": "InnerText11"}},
    {"number": 12.0, "text": "Text12", "inner_object": {"inner_text": "InnerText12"}},
]

OBJECT_ARRAY_13_16 = [
    {"number": 13.0, "text": "Text13", "inner_object": {"inner_text": "InnerText13"}},
    {"number": 14.0, "text": "Text14", "inner_object": {"inner_text": "InnerText14"}},
    {"number": 15.0, "text": "Text15", "inner_object": {"inner_text": "InnerText15"}},
    {"number": 16.0, "text": "Text16", "inner_object": {"inner_text": "InnerText16"}},
]


SAMPLE_DATA = {
    "TextColumn": ["Row1", "Row2", "Row3", "Row4"],
    "IntColumn": [25, 30, 35, 40],
    "FloatColumn": [1.0, 2.0, 3.0, 4.0],
    "ObjectColumn": OBJECT_ARRAY_1_4,
    "ObjectColumnNestedArray": [
        {
            "ArrayProperty": OBJECT_ARRAY_1_4,
        },
        {
            "ArrayProperty": OBJECT_ARRAY_5_8,
        },
        {
            "ArrayProperty": OBJECT_ARRAY_9_12,
        },
        {
            "ArrayProperty": OBJECT_ARRAY_13_16,
        },
    ],
    "ArrayColumn": [
        OBJECT_ARRAY_1_4,
        OBJECT_ARRAY_5_8,
        OBJECT_ARRAY_9_12,
        OBJECT_ARRAY_13_16,
    ],
    "ArrayColumnNestedArray": [
        [
            {
                "ArrayProperty": OBJECT_ARRAY_1_4,
            },
        ],
        [
            {
                "ArrayProperty": OBJECT_ARRAY_5_8,
            },
        ],
        [
            {
                "ArrayProperty": OBJECT_ARRAY_9_12,
            },
        ],
        [
            {
                "ArrayProperty": OBJECT_ARRAY_13_16,
            },
        ],
    ],
}


def generate_json_schema(data):
    def infer_type(value):
        if isinstance(value, dict):
            return {
                "type": "object",
                "properties": {k: infer_type(v) for k, v in value.items()},
            }
        elif isinstance(value, list):
            return {
                "type": "array",
                "items": infer_type(value[0]) if value else {},
            }
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, bool):
            return {"type": "boolean"}
        else:
            return {"type": "null"}

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {k: infer_type(v) for k, v in data.items()},
    }
    return schema
