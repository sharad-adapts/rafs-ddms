import boto3
from loguru import logger
import os
from datetime import datetime, timezone, timedelta
from app.providers.dependencies.blob_loader import IBlobLoader
from urllib.parse import urlparse

TIME_LIMIT_MIN = timedelta(hours=0, minutes=3)
sts_client = boto3.client('sts')

CREDENTIALS_CACHE = {}
def refresh_credentials():
    assumed_role_object=sts_client.assume_role(
            RoleArn=os.environ.get("FILE_CRED_ROLE_ARN"),
            RoleSessionName="AssumeRoleSession1"
        )
    credentials = assumed_role_object['Credentials']
    CREDENTIALS_CACHE["credentials"]=credentials
    CREDENTIALS_CACHE["s3_resource"]=boto3.resource(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    CREDENTIALS_CACHE["expiration"] = credentials['Expiration']

refresh_credentials()
class BlobLoader(IBlobLoader):
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
        return s3_obj.get()['Body'].read()
