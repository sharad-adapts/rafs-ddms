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
from app.api.routes import healthz, info
from app.api.routes.cappressure import api as cappressure_api
from app.api.routes.cce import api as cce_api
from app.api.routes.compositionalanalysis import (
    api as compositionalanalysis_api,
)
from app.api.routes.cvd import api as cvd_api
from app.api.routes.dif_lib import api as dif_lib_api
from app.api.routes.electricalproperties import api as electricalproperties_api
from app.api.routes.extraction import api as extraction_api
from app.api.routes.fractionation import api as fractionation_api
from app.api.routes.interfacialtension import api as interfacialtension_api
from app.api.routes.master_data import coring_api, rocksample_api
from app.api.routes.mcm import api as mcm_api
from app.api.routes.multistageseparator import api as mss_api
from app.api.routes.physchem import api as physchem_api
from app.api.routes.pvt import api as pvt_api
from app.api.routes.relativepermeability import api as relative_permeability_api
from app.api.routes.rocksampleanalysis import api as rocksampleanalysis_api
from app.api.routes.samplesanalysesreport import (
    api as samples_analyses_report_api,
)
from app.api.routes.slimtubetest import api as slimtubetest_api
from app.api.routes.sto import api as sto_api
from app.api.routes.swelling import api as swelling_api
from app.api.routes.transport_test import api as transport_test_api
from app.api.routes.vle import api as vle_api
from app.api.routes.wateranalysis import api as wateranalysis_api

COMMON_DEPENDENCIES = [
    Depends(require_data_partition_id),
]

router = APIRouter()
router.include_router(info.router, tags=["info"])
router.include_router(healthz.router, tags=["healthz"])
router.include_router(
    rocksampleanalysis_api.router,
    tags=["rocksampleanalyses"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(coring_api.router, tags=["coringreports"], dependencies=COMMON_DEPENDENCIES)
router.include_router(rocksample_api.router, tags=["rocksamples"], dependencies=COMMON_DEPENDENCIES)
router.include_router(pvt_api.router, tags=["pvtreports"], dependencies=COMMON_DEPENDENCIES)
router.include_router(cce_api.router, tags=["ccereports"], dependencies=COMMON_DEPENDENCIES)
router.include_router(dif_lib_api.router, tags=["difflibreports"], dependencies=COMMON_DEPENDENCIES)
router.include_router(
    transport_test_api.router,
    tags=["transporttests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    compositionalanalysis_api.router,
    tags=["compositionalanalysisreports"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    mss_api.router,
    tags=["multistageseparatortests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(swelling_api.router, tags=["swellingtests"], dependencies=COMMON_DEPENDENCIES)
router.include_router(
    cvd_api.router,
    tags=["constantvolumedepletiontests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    wateranalysis_api.router,
    tags=["wateranalysisreports"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    sto_api.router,
    tags=["stocktankoilanalysisreports"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    interfacialtension_api.router,
    tags=["interfacialtensiontests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    vle_api.router,
    tags=["vaporliquidequilibriumtests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    mcm_api.router,
    tags=["multiplecontactmiscibilitytests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    slimtubetest_api.router,
    tags=["slimtubetests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    samples_analyses_report_api.router,
    tags=["samplesanalysesreport"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    cappressure_api.router,
    tags=["capillarypressuretests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    relative_permeability_api.router,
    tags=["relativepermeabilitytests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    fractionation_api.router,
    tags=["fractionationtests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    extraction_api.router,
    tags=["extractiontests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    physchem_api.router,
    tags=["physicalchemistrytests"],
    dependencies=COMMON_DEPENDENCIES,
)
router.include_router(
    electricalproperties_api.router,
    tags=["electricalproperties"],
    dependencies=COMMON_DEPENDENCIES,
)
