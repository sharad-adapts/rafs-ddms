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

from fastapi import APIRouter, Depends

from app.api.dependencies.request import require_data_partition_id
from app.api.routes.master_data import coring_api, rocksample_api
from app.api.routes.samplesanalysesreport import (
    api as samples_analyses_report_api,
)
from app.api.routes.v1.cappressure import api as cappressure_api
from app.api.routes.v1.cce import api as cce_api
from app.api.routes.v1.compositionalanalysis import (
    api as compositionalanalysis_api,
)
from app.api.routes.v1.cvd import api as cvd_api
from app.api.routes.v1.dif_lib import api as dif_lib_api
from app.api.routes.v1.electricalproperties import (
    api as electricalproperties_api,
)
from app.api.routes.v1.extraction import api as extraction_api
from app.api.routes.v1.formationresistivityindex import (
    api as formationresistivityindex_api,
)
from app.api.routes.v1.fractionation import api as fractionation_api
from app.api.routes.v1.interfacialtension import api as interfacialtension_api
from app.api.routes.v1.mcm import api as mcm_api
from app.api.routes.v1.multistageseparator import api as mss_api
from app.api.routes.v1.physchem import api as physchem_api
from app.api.routes.v1.pvt import api as pvt_api
from app.api.routes.v1.relativepermeability import (
    api as relative_permeability_api,
)
from app.api.routes.v1.rockcompressibility import api as rockcompressibility_api
from app.api.routes.v1.rocksampleanalysis import api as rocksampleanalysis_api
from app.api.routes.v1.slimtubetest import api as slimtubetest_api
from app.api.routes.v1.sto import api as sto_api
from app.api.routes.v1.swelling import api as swelling_api
from app.api.routes.v1.transport_test import api as transport_test_api
from app.api.routes.v1.vle import api as vle_api
from app.api.routes.v1.wateranalysis import api as wateranalysis_api
from app.api.routes.v1.watergasrelativepermeability import (
    api as watergasrelativepermeability_api,
)

COMMON_DEPENDENCIES = [
    Depends(require_data_partition_id),
]

router = APIRouter()

router.include_router(
    rocksampleanalysis_api.rca_router,
    prefix="/rocksampleanalyses",
    tags=["rocksampleanalyses (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    coring_api.coring_router,
    prefix="/coringreports",
    tags=["coringreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    rocksample_api.rocksample_router,
    prefix="/rocksamples",
    tags=["rocksamples"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    pvt_api.pvt_record_router,
    prefix="/pvtreports",
    tags=["pvtreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    cce_api.cce_router,
    prefix="/ccereports",
    tags=["ccereports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    dif_lib_api.dif_lib_router,
    prefix="/difflibreports",
    tags=["difflibreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    transport_test_api.transport_test_router,
    prefix="/transporttests",
    tags=["transporttests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    compositionalanalysis_api.ca_router,
    prefix="/compositionalanalysisreports",
    tags=["compositionalanalysisreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    mss_api.mss_router,
    prefix="/multistageseparatortests",
    tags=["multistageseparatortests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    swelling_api.swelling_test_router,
    prefix="/swellingtests",
    tags=["swellingtests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    cvd_api.cvd_router,
    prefix="/constantvolumedepletiontests",
    tags=["constantvolumedepletiontests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    wateranalysis_api.wateranalysis_router,
    prefix="/wateranalysisreports",
    tags=["wateranalysisreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    sto_api.sto_router,
    prefix="/stocktankoilanalysisreports",
    tags=["stocktankoilanalysisreports (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    interfacialtension_api.interfacialtension_router,
    prefix="/interfacialtensiontests",
    tags=["interfacialtensiontests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    vle_api.vle_router,
    prefix="/vaporliquidequilibriumtests",
    tags=["vaporliquidequilibriumtests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    mcm_api.mcm_router,
    prefix="/multiplecontactmiscibilitytests",
    tags=["multiplecontactmiscibilitytests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    slimtubetest_api.slimtubetest_router,
    prefix="/slimtubetests",
    tags=["slimtubetests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    samples_analyses_report_api.sar_record_router_v1,
    prefix="/samplesanalysesreport",
    tags=["samplesanalysesreport (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    cappressure_api.cap_pressure_router,
    prefix="/capillarypressuretests",
    tags=["capillarypressuretests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    relative_permeability_api.rel_perm_router,
    prefix="/relativepermeabilitytests",
    tags=["relativepermeabilitytests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    fractionation_api.fractionation_router,
    prefix="/fractionationtests",
    tags=["fractionationtests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    extraction_api.extraction_router,
    prefix="/extractiontests",
    tags=["extractiontests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    physchem_api.physchem_router,
    prefix="/physicalchemistrytests",
    tags=["physicalchemistrytests (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    electricalproperties_api.electrical_properties_router,
    prefix="/electricalproperties",
    tags=["electricalproperties (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    rockcompressibility_api.rockcompressibility_router,
    prefix="/rockcompressibilities",
    tags=["rockcompressibilities (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    watergasrelativepermeability_api.watergasrelativepermeability_router,
    prefix="/watergasrelativepermeabilities",
    tags=["watergasrelativepermeabilities (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    formationresistivityindex_api.formationresistivityindex_router,
    prefix="/formationresistivityindexes",
    tags=["formationresistivityindexes (deprecated)"],
    dependencies=COMMON_DEPENDENCIES,
)
