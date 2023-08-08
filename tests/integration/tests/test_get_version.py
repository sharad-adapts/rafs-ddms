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
import time

import pytest
from starlette import status

from tests.integration.config import DataFiles, DataTemplates, DataTypes


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
        (DataFiles.SAR, DataTypes.SAR, DataTemplates.ID_SAR),
        (DataFiles.CAP_PRESSURE, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
)
@pytest.mark.smoke
def test_get_version(api, helper, create_record, api_path, data_file_name, id_template):
    record_data, created_record = create_record(api_path, data_file_name, id_template)
    version = helper.parse_full_record_id(created_record["recordIdVersions"][0])["version"]
    test_data = getattr(api, api_path).get_record_version(
        record_data["id"], version,
    )

    assert test_data["id"] == record_data["id"]
    assert test_data["version"] == version


@pytest.mark.parametrize(
    "data_file_name, api_path, id_template", [
        (DataFiles.RS, DataTypes.RS, DataTemplates.ID_RS),
        (DataFiles.CORING, DataTypes.CORING, DataTemplates.ID_CORING),
        (DataFiles.RSA, DataTypes.RSA, DataTemplates.ID_RSA),
        (DataFiles.PVT, DataTypes.PVT, DataTemplates.ID_PVT),
        (DataFiles.CCE, DataTypes.CCE, DataTemplates.ID_CCE),
        (DataFiles.DIF_LIB, DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataFiles.CA, DataTypes.CA, DataTemplates.ID_CA),
        (DataFiles.CVD, DataTypes.CVD, DataTemplates.ID_CVD),
        (DataFiles.IT, DataTypes.IT, DataTemplates.ID_IT),
        (DataFiles.MSS, DataTypes.MSS, DataTemplates.ID_MSS),
        (DataFiles.MCM, DataTypes.MCM, DataTemplates.ID_MCM),
        (DataFiles.SLIM_TUBE, DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataFiles.STOA, DataTypes.STOA, DataTemplates.ID_STOA),
        (DataFiles.ST, DataTypes.ST, DataTemplates.ID_ST),
        (DataFiles.TT, DataTypes.TT, DataTemplates.ID_TT),
        (DataFiles.VLE, DataTypes.VLE, DataTemplates.ID_VLE),
        (DataFiles.WA, DataTypes.WA, DataTemplates.ID_WA),
        (DataFiles.SAR, DataTypes.SAR, DataTemplates.ID_SAR),
        (DataFiles.CAP_PRESSURE, DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.EXTRACTION, DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.FRACTIONATION, DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.PHYS_CHEM, DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataFiles.RP, DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
)
@pytest.mark.smoke
def test_get_non_existent_version_of_the_record(api, create_record, api_path, data_file_name, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    int(time.time())
    error = getattr(api, api_path).get_record_version(
        record_data["id"],
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"can't be found for record {record_data['id']}" in error["message"]


@pytest.mark.parametrize(
    "api_path, id_template", [
        (DataTypes.RS, DataTemplates.ID_RS),
        (DataTypes.CORING, DataTemplates.ID_CORING),
        (DataTypes.RSA, DataTemplates.ID_RSA),
        (DataTypes.PVT, DataTemplates.ID_PVT),
        (DataTypes.CCE, DataTemplates.ID_CCE),
        (DataTypes.DIF_LIB, DataTemplates.ID_DIF_LIB),
        (DataTypes.CA, DataTemplates.ID_CA),
        (DataTypes.CVD, DataTemplates.ID_CVD),
        (DataTypes.IT, DataTemplates.ID_IT),
        (DataTypes.MSS, DataTemplates.ID_MSS),
        (DataTypes.MCM, DataTemplates.ID_MCM),
        (DataTypes.SLIM_TUBE, DataTemplates.ID_SLIM_TUBE),
        (DataTypes.STOA, DataTemplates.ID_STOA),
        (DataTypes.ST, DataTemplates.ID_ST),
        (DataTypes.TT, DataTemplates.ID_TT),
        (DataTypes.VLE, DataTemplates.ID_VLE),
        (DataTypes.WA, DataTemplates.ID_WA),
        (DataTypes.SAR, DataTemplates.ID_SAR),
        (DataTypes.CAP_PRESSURE, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataTypes.EXTRACTION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataTypes.FRACTIONATION, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataTypes.PHYS_CHEM, DataTemplates.ID_SAMPLE_ANALYSIS),
        (DataTypes.RP, DataTemplates.ID_SAMPLE_ANALYSIS),
    ],
)
@pytest.mark.smoke
def test_get_version_of_non_existent_record(api, helper, api_path, id_template):
    non_existent_id = f"{id_template}{helper.generate_random_record_id()}"
    error = getattr(api, api_path).get_record_version(
        non_existent_id,
        version=int(time.time()),
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
    assert f"The record '{non_existent_id}' was not found" in error["message"]
