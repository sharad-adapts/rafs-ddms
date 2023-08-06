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
from client.api.core.cap_pressure import CapPressureCore
from client.api.core.cce import CCECore
from client.api.core.compositional_analysis import CompositionalAnalysisCore
from client.api.core.constant_volume_depletion import (
    ConstantVolumeDepletionCore,
)
from client.api.core.coring import CoringCore
from client.api.core.dif_lib import DifLibCore
from client.api.core.extraction import ExtractionCore
from client.api.core.fractionation import FractionationCore
from client.api.core.interfacial_tension import InterfacialTensionCore
from client.api.core.multi_stage_separator import MultiStageSeparatorCore
from client.api.core.multiple_contact_miscibility import (
    MultipleContactMiscibilityCore,
)
from client.api.core.phys_chem import PhysChemCore
from client.api.core.pvt import PVTCore
from client.api.core.relative_permeability import RelativePermeabilityCore
from client.api.core.rock_sample import RockSampleCore
from client.api.core.rock_sample_analysis import RSACore
from client.api.core.samples_analyses_report import SamplesAnalysesReportCore
from client.api.core.slim_tube import SlimTubeCore
from client.api.core.stock_tank_oil_analysis import StockTankOilAnalysisCore
from client.api.core.swelling_test import SwellingTestCore
from client.api.core.transport_test import TransportTestCore
from client.api.core.vapor_liquid_equilibrium import VaporLiquidEquilibriumCore
from client.api.core.water_analysis import WaterAnalysisCore
from client.api.legal import APILegal
from client.api.storage import APIStorage


class ApiWorker(object):
    """Class combine all api actions in one place."""

    def __init__(self, host: str, url_prefix: str, data_partition: str, token: str) -> None:
        self.storage = APIStorage(host, data_partition, token)
        self.legal = APILegal(host, data_partition, token)
        self.rsa = RSACore(host, url_prefix, data_partition, token)
        self.rs = RockSampleCore(host, url_prefix, data_partition, token)
        self.coring = CoringCore(host, url_prefix, data_partition, token)
        self.pvt = PVTCore(host, url_prefix, data_partition, token)
        self.cce = CCECore(host, url_prefix, data_partition, token)
        self.dif_lib = DifLibCore(host, url_prefix, data_partition, token)
        self.ca = CompositionalAnalysisCore(host, url_prefix, data_partition, token)
        self.cvd = ConstantVolumeDepletionCore(host, url_prefix, data_partition, token)
        self.st = SwellingTestCore(host, url_prefix, data_partition, token)
        self.mss = MultiStageSeparatorCore(host, url_prefix, data_partition, token)
        self.tt = TransportTestCore(host, url_prefix, data_partition, token)
        self.stoa = StockTankOilAnalysisCore(host, url_prefix, data_partition, token)
        self.wa = WaterAnalysisCore(host, url_prefix, data_partition, token)
        self.it = InterfacialTensionCore(host, url_prefix, data_partition, token)
        self.vle = VaporLiquidEquilibriumCore(host, url_prefix, data_partition, token)
        self.slim_tube = SlimTubeCore(host, url_prefix, data_partition, token)
        self.mcm = MultipleContactMiscibilityCore(host, url_prefix, data_partition, token)
        self.sar = SamplesAnalysesReportCore(host, url_prefix, data_partition, token)
        self.cap_pressure = CapPressureCore(host, url_prefix, data_partition, token)
        self.extraction = ExtractionCore(host, url_prefix, data_partition, token)
        self.fractionation = FractionationCore(host, url_prefix, data_partition, token)
        self.rp = RelativePermeabilityCore(host, url_prefix, data_partition, token)
        self.phys_chem = PhysChemCore(host, url_prefix, data_partition, token)
