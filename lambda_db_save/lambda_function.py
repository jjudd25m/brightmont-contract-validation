import json
import boto3
import psycopg2
from urllib.parse import urlparse
from validators.agreement_validator import check_agreement_data


def get_secret(secret_parameter):
    secret_name = "prod-brightmont-backend-env"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
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
        _conn.autocommit = True
    return _conn

def upsert_agreement(conn, agreement, s3_path):
    """
    Insert or update an agreement by s3_path.
    Returns agreement.id
    """

    upsert_agreement_sql = """
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
        is_valid,
        document_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        is_valid = EXCLUDED.is_valid,
        document_id = EXCLUDED.document_id
    RETURNING id;
    """

    insert_service_sql = """
    INSERT INTO public.agreement_services (
        service_name,
        cost_per_unit,
        units,
        tuition
    )
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """

    delete_links_sql = """
    DELETE FROM public.agreements_service_agreements
    WHERE agreement_id = %s;
    """

    insert_link_sql = """
    INSERT INTO public.agreements_service_agreements (agreement_id, agreement_service_id)
    VALUES (%s, %s)
    RETURNING id;
    """

    services = agreement["services_list"] or []

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                upsert_agreement_sql,
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
                    int(agreement["current_grade"] or 0),
                    float(agreement["total_tuition"] or 0),
                    int(agreement["one_to_one_sessions"] or 0),
                    int(agreement["homework_studio_sessions"] or 0),
                    str(agreement["scheduled_start_date"]),
                    agreement["scholarship_type"],
                    agreement["scholarship_payment"],
                    bool(agreement["is_single_payment"] or False),
                    float(agreement["payment_amount"] or 0),
                    agreement["is_human_approved"],
                    agreement["is_valid"],
                    agreement["document_id"]
                ),
            )

            agreement_id = cur.fetchone()[0]
            # 2) Clear existing links (so DB matches current extracted services)
            cur.execute(delete_links_sql, (agreement_id,))

            # 3) Upsert each service and re-link
            for s in services:
                service_name = s["service_name"]
                cost_per_unit = float(s["cost_per_unit"] or 0)
                units = int(s["units"] or 0)
                tuition = float(s["tuition"] or 0)

                cur.execute(
                    insert_service_sql,
                    (service_name, cost_per_unit, units, tuition),
                )
                service_id = cur.fetchone()[0]

                cur.execute(insert_link_sql, (agreement_id, service_id))

    return agreement_id


def lambda_handler(event, context):
    print(event)
    if event.get("invoke_from_extract"):
        agreement = event.get("agreement")
        path_value = event.get("s3_path")
        agreement["s3_path"] = path_value
        agreement["input_format"] = "extracted from model"

        valid_data, agreement = check_agreement_data(**agreement)

        conn = get_conn()
        agreement_dict = agreement.model_dump()

        try:
            print(f"UPDATE...{agreement_dict}")
            upsert_agreement(conn, agreement_dict, path_value)
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
            try:
                conn.close()
            except Exception:
                pass
            raise

    else:
        qs_params = event.get("queryStringParameters") or {}
        path_value = qs_params.get("s3_path")  # will be None if not provided
        method = event["httpMethod"]

        if method == "PUT":
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
            agreement["s3_path"] = path_value

            agreement["input_format"] = "user save"

            valid_data, agreement = check_agreement_data(**agreement)

            conn = get_conn()

            print(agreement)
            print(type(agreement))
            agreement_dict = agreement.model_dump()

            try:
                print(f"UPDATE... {agreement_dict}")
                upsert_agreement(conn, agreement_dict, path_value)
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
