import json
import boto3
from botocore.exceptions import ClientError
import psycopg2
from urllib.parse import urlparse
from datetime import date, datetime
import os

SECRET_NAME = os.getenv("APP_SECRET_NAME")

def convert(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def get_secret(secret_parameter):
    secret = boto3.client("secretsmanager")

    try:
        get_secret_value_response = secret.get_secret_value(
            SecretId=SECRET_NAME
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    secret = json.loads(secret)
    return secret[secret_parameter]

_conn = None
DB_URL = get_secret("DATABASE_URL")

def get_conn():
    global _conn
    if _conn is None or _conn.closed:
        url = urlparse(DB_URL)
        _conn = psycopg2.connect(
            dbname=url.path.lstrip("/"),
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port or 5432,
            connect_timeout=5,
        )
        _conn.autocommit = True  # or manage commit/rollback explicitly
    return _conn

def upsert_agreement(conn, agreement, s3_path):
    """
    Insert or update an agreement by s3_path.
    Returns agreement.id
    """

    sql = """
    INSERT INTO public.agreements (
        s3_path,
        document_title,
        student_first_name,
        student_last_name,
        student_nickname,
        parent_guardian_full_name,
        parent_guardian_email,
        second_parent_guardian_full_name,
        second_parent_guardian_email,
        student_courses,
        student_campus,
        student_college_bound,
        current_grade,
        total_tuition,
        one_to_one_sessions,
        homework_studio_sessions,
        scheduled_start_date,
        scholarship_type,
        scholarship_payment,
        is_single_payment,
        payment_amount,
        is_human_approved,
        document_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (s3_path)
    DO UPDATE SET
        document_title = EXCLUDED.document_title,
        student_first_name = EXCLUDED.student_first_name,
        student_last_name = EXCLUDED.student_last_name,
        student_nickname = EXCLUDED.student_nickname,
        parent_guardian_full_name = EXCLUDED.parent_guardian_full_name,
        parent_guardian_email = EXCLUDED.parent_guardian_email,
        second_parent_guardian_full_name = EXCLUDED.second_parent_guardian_full_name,
        second_parent_guardian_email = EXCLUDED.second_parent_guardian_email,
        student_courses = EXCLUDED.student_courses,
        student_campus = EXCLUDED.student_campus,
        student_college_bound = EXCLUDED.student_college_bound,
        current_grade = EXCLUDED.current_grade,
        total_tuition = EXCLUDED.total_tuition,
        one_to_one_sessions = EXCLUDED.one_to_one_sessions,
        homework_studio_sessions = EXCLUDED.homework_studio_sessions,
        scheduled_start_date = EXCLUDED.scheduled_start_date,
        scholarship_type = EXCLUDED.scholarship_type,
        scholarship_payment = EXCLUDED.scholarship_payment,
        is_single_payment = EXCLUDED.is_single_payment,
        payment_amount = EXCLUDED.payment_amount,
        is_human_approved = TRUE,
        document_id = EXCLUDED.document_id
    RETURNING id;
    """

    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                s3_path,
                agreement["document_title"],
                agreement["student_first_name"],
                agreement["student_last_name"],
                agreement["student_nickname"],
                agreement["parent_guardian_full_name"],
                agreement["parent_guardian_email"],
                agreement["second_parent_guardian_full_name"],
                agreement["second_parent_guardian_email"],
                agreement["student_courses"],
                agreement["student_campus"],
                agreement["student_college_bound"],
                agreement["current_grade"],
                agreement["total_tuition"],
                agreement["one_to_one_sessions"],
                agreement["homework_studio_sessions"],
                agreement["scheduled_start_date"],
                agreement["scholarship_type"],
                agreement["scholarship_payment"],
                agreement["is_single_payment"],
                agreement["payment_amount"],
                True,
                agreement["document_id"]
            ),
        )

        agreement_id = cur.fetchone()[0]
    return agreement_id


def lambda_handler(event, context):
    qs_params = event.get("queryStringParameters") or {}
    path_value = qs_params.get("s3_path")  # will be None if not provided
    method = event["httpMethod"]

    DB_URL = get_secret("DATABASE_URL")

    if method == "GET":
        if not path_value:
            try:
                url = urlparse(DB_URL)
                conn = psycopg2.connect(
                    dbname=url.path.lstrip('/'),
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port or 5432,
                    connect_timeout=5,
                )
                cur = conn.cursor()
                cur.execute("SELECT * FROM public.agreements;")
                rows = cur.fetchall()

                colnames = [desc[0] for desc in cur.description]

                cur.close()
                conn.close()

                results = [
                    {col: convert(val) for col, val in zip(colnames, row)}
                    for row in rows
                ]
                results = [result["s3_path"] for result in results if result.get("s3_path")]

                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true"
                    },
                    "body": json.dumps(results)
                }

            except Exception as e:
                return {
                    "statusCode": 500,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true"
                    },
                    "body": json.dumps({"ok": False, "error": str(e)})
                }
        if path_value:
            print(f"There is path value: {path_value}")
            try:
                url = urlparse(DB_URL)
                conn = psycopg2.connect(
                    dbname=url.path.lstrip('/'),
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port or 5432,
                    connect_timeout=5,
                )
                sql = """
                    SELECT
                    a.*,
                    COALESCE(
                        json_agg(s.*) FILTER (WHERE s.id IS NOT NULL),
                        '[]'::json
                    ) AS services
                    FROM public.agreements a
                    LEFT JOIN public.agreements_service_agreements asa
                    ON asa.agreement_id = a.id
                    LEFT JOIN public.agreement_services s
                    ON s.id = asa.agreement_service_id
                    WHERE a.s3_path = %s
                    GROUP BY a.id;
                    """

                cur = conn.cursor()
                """
                cur.execute(
                    "SELECT * FROM public.agreements WHERE s3_path = %s;",
                    (path_value,)
                )
                """
                cur.execute(sql, (path_value,))

                row = cur.fetchone()
                colnames = [desc[0] for desc in cur.description]

                cur.close()
                conn.close()

                # result = dict(zip(colnames, row))
                results = {col: val for col, val in zip(colnames, row)}

                print(results)
                # results["created_at"] = results["created_at"].isoformat()
                # results["updated_at"] = results["updated_at"].isoformat()
                # results["deleted_at"] = results["deleted_at"].isoformat()
                results.pop("created_at")
                results.pop("updated_at")
                results.pop("deleted_at")

                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true"
                    },
                    "body": json.dumps(results)
                }

            except Exception as e:
                print(f"ERROR: {e}")
                return {
                    "statusCode": 500,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": "true"
                    },
                    "body": json.dumps({"ok": False, "error": str(e)})
                }
    elif method == "PUT":
        if not path_value:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                },
                "body": json.dumps("Path value is mandatory")
            }

        agreement = json.loads(event["body"])
        conn = get_conn()

        try:
            print("UPDATE...")
            upsert_agreement(conn, agreement, path_value)
            print("UPDATED")
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
            # optionally force reconnect next time:
            try:
                conn.close()
            except Exception:
                pass
            raise
