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

import json
import os
from typing import Union

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_EXAMPLES_DIR = os.path.join(BASE_DIR, "..", "models", "examples")


def load_data_example(file_name: str) -> Union[list, dict]:
    """Loads data examples.

    :param str file_name: the filename
    :return Union[list, dict]: an example of data
    """
    with open(os.path.join(MODELS_EXAMPLES_DIR, file_name), "r") as json_file:
        return json.load(json_file)
