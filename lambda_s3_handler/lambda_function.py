import boto3
import base64
import json
import os

s3 = boto3.client('s3')
BUCKET = os.getenv("PDF_BUCKET")

def lambda_handler(event, context):
    try:
        qs_params = event.get("queryStringParameters") or {}
        path_value = qs_params.get("s3_path")
        print(f"There is a path value: {path_value}")

        if not path_value:
            print("Error: There is no s3_path")

        else:
            print("START DOWNLOADING...")
            # 1) Download PDF from S3 into memory
            obj = s3.get_object(Bucket=BUCKET, Key=path_value)
            pdf_bytes = obj["Body"].read()

            # 2) Base64-encode for API Gateway binary support
            encoded = base64.b64encode(pdf_bytes).decode("utf-8")

            # 3) Return as binary response to API Gateway
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                },
                "body": encoded
            }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            },
            "body": json.dumps({"ok": False, "error": str(e)})
        }
