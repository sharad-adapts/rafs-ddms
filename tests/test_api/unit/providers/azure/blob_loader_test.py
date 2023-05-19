#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.providers.dependencies.az.blob_loader import (
    TIMEOUT,
    BlobClient,
    BlobLoader,
)

TEST_BLOB_URL = "https://somedomain.blob.core.windows.net/staging-area/user"
TEST_BLOB = b"blob"


class TestBlobLoader:
    @pytest.mark.asyncio
    async def test_upload_blob(self):
        # Patch the BlobClient.upload_blob method to return a mock response
        with patch.object(BlobClient, "upload_blob", return_value=Mock()) as blob_client:
            blob_loader = BlobLoader()
            response = await blob_loader.upload_blob(TEST_BLOB_URL, TEST_BLOB)
        # Verify response and blob client called
        assert response is None
        blob_client.assert_called_once_with(blob_type="BlockBlob", data=TEST_BLOB, overwrite=True, timeout=TIMEOUT)

    @pytest.mark.asyncio
    async def test_download_blob(self):
        # Patch the BlobClient.download_blob method to return a mock response
        with patch.object(BlobClient, "download_blob", return_value=AsyncMock(readall=AsyncMock(return_value=TEST_BLOB))) as blob_client:
            blob_loader = BlobLoader()
            response = await blob_loader.download_blob(TEST_BLOB_URL)
        # Verify response and blob client called
        assert response == TEST_BLOB
        blob_client.assert_called_once_with(timeout=TIMEOUT)
