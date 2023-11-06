# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the “License”).
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import boto3

from app.providers.dependencies.blob_loader import IBlobLoader

TIME_LIMIT_MIN = timedelta(hours=0, minutes=3)
sts_client = boto3.client("sts")

CREDENTIALS_CACHE = {}


def refresh_credentials():
    assumed_role_object = sts_client.assume_role(
        RoleArn=os.environ.get("FILE_CRED_ROLE_ARN"),
        RoleSessionName="AssumeRoleSession1",
    )
    credentials = assumed_role_object["Credentials"]
    CREDENTIALS_CACHE["credentials"] = credentials
    CREDENTIALS_CACHE["s3_resource"] = boto3.resource(
        "s3",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    CREDENTIALS_CACHE["expiration"] = credentials["Expiration"]


refresh_credentials()


class AWSBlobLoader(IBlobLoader):
    def __init__(self):
        now = datetime.now(timezone.utc)
        if now > CREDENTIALS_CACHE["expiration"] - TIME_LIMIT_MIN:
            refresh_credentials()
        self.s3_resource = CREDENTIALS_CACHE["s3_resource"]

    def client_from_url(self, signed_url: str):
        parse_result = urlparse(signed_url)
        bucket_endpoint = parse_result.netloc
        key = parse_result.path.lstrip("/")
        bucket = bucket_endpoint.split(".")[0]
        return self.s3_resource.Object(bucket, key)

    async def upload_blob(self, upload_url: str, blob: bytes):
        s3_obj = self.client_from_url(upload_url)
        return s3_obj.put(Body=blob)

    async def download_blob(self, download_url: str) -> bytes:
        s3_obj = self.client_from_url(download_url)
        return s3_obj.get()["Body"].read()
