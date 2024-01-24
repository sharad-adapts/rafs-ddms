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

import io
import json

import boto3
import pytest
from botocore.response import StreamingBody
from botocore.stub import Stubber

from app.providers.dependencies.aws.blob_loader import AWSBlobLoader

TEST_BUCKET = "test-bucket"
TEST_KEY = "opendes/abc/123"
TEST_BLOB_URL = f"https://{TEST_BUCKET}.s3.us-east-1.amazonaws.com/{TEST_KEY}?Param=p"
TEST_BLOB = b"blob"

expected_message = {
    "message": "blob"
}

encoded_message = json.dumps(expected_message).encode()
raw_stream = StreamingBody(
    io.BytesIO(encoded_message),
    len(encoded_message)
)

get_response = {
    "Body": raw_stream
}

put_response = {
    "ETag": "6805f2cfc46c0f04559748bb039d69ae",
    "VersionId": "Bvq0EDKxOcXLJXNo_Lkz37eM3R4pfzyQ",
    "ResponseMetadata": {
        "RequestId": "abc123",
        "HTTPStatusCode": 200,
        "HostId": "abc123"
    },
}

s3 = boto3.client("s3")
s3_stub = Stubber(s3)
expected_params = {
    "Bucket": TEST_BUCKET,
    "Key": TEST_KEY,
}
# s3_stub.add_response("put_object", put_response, expected_params)
s3_stub.add_response("get_object", get_response)
s3_stub.activate()


class TestBlobLoader:

    # @pytest.mark.asyncio
    # async def test_upload_blob(self):
    #     blob_loader = AWSBlobLoader(s3)
    #     upload_response = await blob_loader.upload_blob(TEST_BLOB_URL, TEST_BLOB)
    #     assert upload_response == put_response

    @pytest.mark.asyncio
    async def test_download_blob(self):
        blob_loader = AWSBlobLoader(s3)
        download_response = await blob_loader.download_blob(TEST_BLOB_URL)
        print(download_response)
        assert download_response == encoded_message
