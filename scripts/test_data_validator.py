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

import argparse
import json
import os
import sys

import pandas as pd
from pydantic.error_wrappers import ValidationError

app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(app_dir)

from app.models.data_schemas.api_v2 import base


def create_test_data_from_example(
    data_example_path: str,
    test_data_path: str,
    model_class_name: str,
):
    """Create test data using pandas after validating the example provided."""

    model = getattr(base, model_class_name)

    with open(data_example_path) as fp:
        example = json.load(fp)

    try:
        for elem in example:
            model.validate(elem)
        pd.read_json(data_example_path, orient="records").to_json(test_data_path, orient="split", indent=2)
    except ValidationError as exc:
        # print errors
        print(str(exc))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process example files, validates and create test data.")
    parser.add_argument("data_example_path", type=str, help="DataExample file path in format orient='records'.")
    parser.add_argument("test_data_path", type=str, help="target test data path")
    parser.add_argument("model_class_name", type=str, help="Class name of the model use for validation.")
    args = parser.parse_args()

    create_test_data_from_example(args.data_example_path, args.test_data_path, args.model_class_name)