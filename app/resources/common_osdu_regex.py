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


REFERENCE_DATA = r"[\"\'\s]{1}[^\s\'\"]+:reference-data\-\-[^\s\'\"]+:[^\s\'\"]+[:]*[^\s\'\"]*[\"\'\s]{1}"
MASTER_DATA = r"[\"\'\s]{1}[^\s\'\"]+:master-data\-\-[^\s\'\"]+:[^\s\'\"]+[:]*[^\s\'\"]*[\"\'\s]{1}"
WPC = r"[\"\'\s]{1}[^\s\'\"]+:work-product-component\-\-[^\s\'\"]+:[^\s\'\"]+[:]*[^\s\'\"]*[\"\'\s]{1}"

ALL_OSDU_REGEXES = [REFERENCE_DATA, MASTER_DATA, WPC]
