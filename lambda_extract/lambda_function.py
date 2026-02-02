import json
import boto3
import tempfile
import os
from llama_cloud_services import LlamaExtract # pip install llama_cloud_services
from llama_cloud import ExtractConfig, ExtractMode, PublicModelName
import pdfplumber
from schemas.registry import titles, EXTRACTION_PLANS, POST_PROCESSING_PLAN, \
    TuitionSchemaFirstPage, TuitionSchemaSecondPage

from aws.client import AwsAdapter

aws = AwsAdapter()

from extract.app import LLMExtractor
extractor = LLMExtractor(
    api_key=aws.get_secret_value("LLAMA_PARSE_API_KEY"),
    extraction_plans=EXTRACTION_PLANS,
    post_processing_plan=POST_PROCESSING_PLAN
)

def lambda_handler(event, context):
    qs_params = event.get("queryStringParameters") or {}
    path_value = qs_params.get("s3_path")

    print(f"Path value: {path_value}")
    if path_value:
        local_file_name = aws.download_pdf_to_tmp(path_value)
        print(f"Processing: {path_value}")
        print(f"Local file name: {local_file_name}")

        agreement = extractor.extract(local_file_name)

        try:
            print(f"UPDATE agreement: {agreement}")
            aws.call_upsert(agreement, path_value)
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                },
                "body": json.dumps("UPDATED")
            }
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
            raise

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": json.dumps(agreement)
        }
