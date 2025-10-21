from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import boto3

from compose_runner.aws_lambda.common import LambdaRequest

_S3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))

RESULTS_BUCKET_ENV = "RESULTS_BUCKET"
RESULTS_PREFIX_ENV = "RESULTS_PREFIX"
DEFAULT_EXPIRES_IN = 900


def _serialize_dt(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    request = LambdaRequest.parse(event)
    payload = request.payload
    bucket = os.environ[RESULTS_BUCKET_ENV]
    prefix = os.environ.get(RESULTS_PREFIX_ENV)

    artifact_prefix = payload.get("artifact_prefix")
    if not artifact_prefix:
        message = "Request payload must include 'artifact_prefix'."
        if request.is_http:
            return request.bad_request(message, status_code=400)
        raise KeyError(message)
    expires_in = int(payload.get("expires_in", DEFAULT_EXPIRES_IN))

    key_prefix = f"{prefix.rstrip('/')}/{artifact_prefix}" if prefix else artifact_prefix

    response = _S3.list_objects_v2(Bucket=bucket, Prefix=key_prefix)
    contents = response.get("Contents", [])

    artifacts: List[Dict[str, Any]] = []
    for obj in contents:
        key = obj["Key"]
        if key.endswith("/"):
            continue
        url = _S3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        artifacts.append(
            {
                "key": key,
                "filename": key.split("/")[-1],
                "size": obj.get("Size"),
                "last_modified": _serialize_dt(obj["LastModified"]),
                "url": url,
            }
        )

    body = {
        "artifact_prefix": artifact_prefix,
        "artifacts": artifacts,
        "bucket": bucket,
        "prefix": key_prefix,
    }
    return request.respond(body)
