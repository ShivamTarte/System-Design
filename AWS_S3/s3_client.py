import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def get_s3_client():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_default_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError(
            "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your environment or .env file"
        )

    client_kwargs = {
        "service_name": "s3",
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "region_name": aws_default_region,
    }

    session_token = os.getenv("AWS_SESSION_TOKEN")
    if session_token:
        client_kwargs["aws_session_token"] = session_token

    return boto3.client(**client_kwargs)


def list_buckets():
    s3_client = get_s3_client()
    response = s3_client.list_buckets()
    return [bucket["Name"] for bucket in response.get("Buckets", [])]


if __name__ == "__main__":
    try:
        buckets = list_buckets()
        print("Connected successfully. Buckets:")
        for bucket in buckets:
            print(f"- {bucket}")
    except Exception as exc:
        print(f"S3 connection failed: {exc}")
