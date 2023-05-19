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

import http
from typing import List
from unittest import mock

import pytest
from fastapi.responses import JSONResponse, StreamingResponse

from app.resources.mime_types import CustomMimeTypes
from app.resources.source_renderer import DatasetSourceFile, FileSourceRenderer


class TestFileSourceRenderer:

    @pytest.mark.asyncio
    async def test_render_source_data_with_multiple_files(self):
        files = [
            DatasetSourceFile(dataset_id="dataset1", mime_type="text/csv", content=b"file1_content"),
            DatasetSourceFile(dataset_id="dataset2", mime_type="application/json", content=b"file2_content"),
        ]
        renderer = FileSourceRenderer(files)
        with mock.patch("zipfile.ZipFile") as mock_zipfile:
            mock_zipfile.return_value = mock.MagicMock()
            response = await renderer.render_source_data()
            assert isinstance(response, StreamingResponse)
            assert response.media_type == "application/zip"
            assert response.headers.get("Content-Disposition") == "attachment;filename=datasets.zip"
            assert response.headers["Content-Type"] == CustomMimeTypes.ZIP.type

    @pytest.mark.asyncio
    async def test_render_source_data_with_single_file(self):
        files = [
            DatasetSourceFile(dataset_id="dataset1", mime_type="text/csv", content=b"file1_content"),
        ]
        renderer = FileSourceRenderer(files)
        response = await renderer.render_source_data()
        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/csv"
        assert response.headers.get("Content-Disposition") == 'attachment;filename="dataset1.csv"'

    @pytest.mark.asyncio
    async def test_render_source_data_with_no_files(self):
        files: List[DatasetSourceFile] = []
        renderer = FileSourceRenderer(files)
        response = await renderer.render_source_data()
        assert isinstance(response, JSONResponse)
        assert response.status_code == http.HTTPStatus.NOT_FOUND
