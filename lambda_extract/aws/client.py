# from __future__ import annotations
import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any, Optional
import boto3
from botocore.exceptions import ClientError


def get_s3_path(event: dict) -> str:
    path_value = (event.get("queryStringParameters") or {}).get("s3_path")
    if path_value:
        return path_value

    if event.get("source") == "aws.s3":
        detail = event.get("detail") or {}
        # bucket = (detail.get("bucket") or {}).get("name")
        key = (detail.get("object") or {}).get("key")
        if key:
            return key

    raise ValueError("Could not determine s3_path from event.")


@dataclass(frozen=True)
class AwsConfig:
    # region: str = os.getenv("REGION")
    upsert_fn: str = os.getenv("UPSERT_FN")
    bucket: str = os.getenv("PDF_BUCKET")
    secret_name: str = os.getenv("APP_SECRET_NAME")


class AwsAdapter:
    def __init__(self, cfg: Optional[AwsConfig] = None, session: Optional[boto3.session.Session] = None):
        self.cfg = cfg if cfg is not None else AwsConfig()
        # self.session = session or boto3.session.Session(region_name=self.cfg.region)

        # Create clients once (reused)
        # self.s3 = self.session.client("s3")
        # self.lambda_client = self.session.client("lambda")
        # self.secrets = self.session.client("secretsmanager")
        self.s3 = boto3.client("s3")
        self.lambda_client = boto3.client("lambda")
        self.secrets = boto3.client("secretsmanager")

    def call_upsert(self, agreement: dict, s3_path: str) -> dict:
        payload = {
            "agreement": agreement,
            "s3_path": s3_path,
            "invoke_from_extract": True,
        }

        return self.lambda_client.invoke(
            FunctionName=self.cfg.upsert_fn,
            InvocationType="Event",
            Payload=json.dumps(payload).encode("utf-8"),
        )

    def get_secret_value(self, secret_parameter: str) -> Any:
        try:
            get_secret_value_response = self.secrets.get_secret_value(
                SecretId=self.cfg.secret_name
            )
        except ClientError as e:
            raise e

        secret = get_secret_value_response["SecretString"]
        secret = json.loads(secret)
        return secret[secret_parameter]

    def download_pdf_to_tmp(self, key: str) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp")
        tmp_path = tmp.name
        tmp.close()

        print(f"Start download s3://{self.cfg.bucket}/{key} -> {tmp_path}")
        with open(tmp_path, "wb") as f:
            self.s3.download_fileobj(self.cfg.bucket, key, f)
            f.flush()
            os.fsync(f.fileno())

        return tmp_path
