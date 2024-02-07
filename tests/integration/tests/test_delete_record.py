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
import pytest
from starlette import status

from tests.integration.config import (
    DataFiles,
    DataTemplates,
    DataTypes,
    SamplesAnalysisTypes,
)


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
def test_delete_record(api, create_record, api_path, data_file_name, id_template):
    record_data, _ = create_record(api_path, data_file_name, id_template)
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    getattr(api, api_path).get_record(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


@pytest.mark.smoke
@pytest.mark.v2
def test_delete_v2_sample_analysis(api, create_record):
    data_file_name = DataFiles.SAMPLE_ANALYSIS
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS

    record_data, _ = create_record(api_path, data_file_name, id_template, "BasicRockProperties")
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(record_data["id"], allowed_codes=[status.HTTP_204_NO_CONTENT])
    getattr(api, api_path).get_record(record_data["id"], allowed_codes=[status.HTTP_404_NOT_FOUND])


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
def test_delete_non_existent_record(api, helper, api_path, id_template):
    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(
        f"{id_template}{helper.generate_random_record_id()}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )


@pytest.mark.smoke
@pytest.mark.v2
def test_delete_v2_sample_analysis_non_existent_record(api, helper, create_record):
    api_path = DataTypes.SAMPLE_ANALYSIS
    id_template = DataTemplates.ID_SAMPLE_ANALYSIS

    # status code check is implemented on the API client layer
    getattr(api, api_path).soft_delete_record(
        f"{id_template}{helper.generate_random_record_id()}",
        allowed_codes=[status.HTTP_404_NOT_FOUND],
    )
