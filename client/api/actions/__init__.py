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

from client.api.actions.cce import CCEAction
from client.api.actions.coring import CoringAction
from client.api.actions.dif_lib import DifLibAction
from client.api.actions.pvt import PVTAction
from client.api.actions.rock_sample import RockSampleAction
from client.api.actions.rock_sample_analysis import RSAAction


class ApiWorker(object):
    """Class combine all api actions in one place."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str) -> None:
        self.rsa = RSAAction(host, url_prefix, data_partition, token)
        self.rs = RockSampleAction(host, url_prefix, data_partition, token)
        self.coring = CoringAction(host, url_prefix, data_partition, token)
        self.pvt = PVTAction(host, url_prefix, data_partition, token)
        self.cce = CCEAction(host, url_prefix, data_partition, token)
        self.dif_lib = DifLibAction(host, url_prefix, data_partition, token)
