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

from pathlib import Path

CONFIG = {}

DATA_DIR = Path("tests", "integration", "data")
RSA_FILE = "rsa.json"
RCA_FILE = "rca.json"
RS_FILE = "rocksample.json"
CORING_FILE = "coring.json"
PVT_FILE = "pvt.json"
CCE_FILE = "cce.json"
CCE_DATA_FILE = "cce_data.json"
DIF_LIB_FILE = "dif_lib.json"
DIF_LIB_DATA_FILE = "dif_lib_data.json"

UPLOADED_FILES = [
    "opendes:dataset--File.Generic:RCA_Norway-VOLVE-NO_15_9-19_A:",
    "opendes:dataset--File.Generic:Schema_Presentation:",
    "opendes:dataset--File.Generic:Kentish_Knock_South-1_Core_Analysis_MSCT_RCA:",
]

# data store between tests
DATA_STORE = {}
