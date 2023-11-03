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

from typing import NamedTuple


class CommonRelativePathsV1(NamedTuple):
    ROUTINECOREANALYSIS: str = "/rocksampleanalyses/"
    CCE: str = "/ccereports/"
    DIF_LIB: str = "/difflibreports/"
    TRANSPORT_TEST: str = "/transporttests/"
    COMPOSITIONAL_ANALYSIS: str = "/compositionalanalysisreports/"
    MSS: str = "/multistageseparatortests/"
    SWELLING: str = "/swellingtests/"
    CVD: str = "/constantvolumedepletiontests/"
    WATER_ANALYSIS: str = "/wateranalysisreports/"
    STO_ANALYSIS: str = "/stocktankoilanalysisreports/"
    INTERFACIAL_TENSION: str = "/interfacialtensiontests/"
    VLE: str = "/vaporliquidequilibriumtests/"
    MCM: str = "/multiplecontactmiscibilitytests/"
    SLIMTUBETEST: str = "/slimtubetests/"
    RELATIVE_PERMEABILITY: str = "/relativepermeabilitytests/"
    CAP_PRESSURE: str = "/capillarypressuretests/"
    FRACTIONATION: str = "/fractionationtests/"
    EXTRACTION: str = "/extractiontests/"
    PHYS_CHEM: str = "/physicalchemistrytests/"
    WATER_GAS_RELATIVE_PERMEABILITY: str = "/watergasrelativepermeabilities/"
    ROCK_COMPRESSIBILITY: str = "/rockcompressibilities/"
    ELECTRICAL_PROPERTIES: str = "/electricalproperties/"
    FORMATION_RESISTIVITY_INDEX: str = "/formationresistivityindexes/"


class CommonRelativePathsV2(NamedTuple):
    ELECTRICAL_PROPERTIES: str = "/data/electricalproperties"
    NMR: str = "/data/nmrtests"
    MULTIPLE_SALINITY: str = "/data/multiplesalinitytests"
    GCMS_ALKANES: str = "/data/gcmsalkanes"
    MERCURY_INJECTION: str = "/data/mercuryinjectionanalyses"
    GCMS_AROMATICS: str = "/data/gcmsaromatics"
    GCMS_RATIOS: str = "/data/gcmsratios"
    GAS_CHROMATOGRAPHY: str = "/data/gaschromatographyanalyses"
    GAS_COMPOSITION: str = "/data/gascompositionanalyses"
    ISOTOPE_ANALYSIS: str = "/data/isotopes"
    BULK_PYROLYSIS: str = "/data/bulkpyrolysisanalyses"
    CORE_GAMMA: str = "/data/coregamma"
    UNIAXIAL_TEST: str = "/data/uniaxial"
    CEC_CONTENT: str = "/data/cec"


COMMON_RELATIVE_PATHS = {
    "v1": CommonRelativePathsV1,
    "v2": CommonRelativePathsV2,
}
